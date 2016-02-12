#!/usr/bin/perl

#┌─────────────────────────────────
#│ WEB MART : order.cgi - 2014/06/22
#│ copyright (c) KentWeb
#│ http://www.kent-web.com/
#└─────────────────────────────────

# モジュール宣言
use strict;
use CGI::Carp qw(fatalsToBrowser);
use lib "./lib";
use CGI::Minimal;
use Jcode;
use Crypt::RC4;

# 設定ファイル取り込み
require './init.cgi';
my %cf = set_init();

# データ受理
CGI::Minimal::max_read_size($cf{maxdata});
my $cgi = CGI::Minimal->new;
cgi_err('容量オーバー') if ($cgi->truncated);
my %in = parse_form($cgi);

# 処理分岐
if ($in{mode} eq "law")  { law_data(); }
if ($in{mode} eq "addr") { addr_form(); }
if ($in{mode} eq "conf") { conf_form(); }
if ($in{mode} eq "send") { send_form(); }
error("不明な処理です");

#-----------------------------------------------------------
#  住所入力画面 (Step1)
#-----------------------------------------------------------
sub addr_form {
	my %er = @_;

	# back属性チェック
	chk_back($in{back});

	# 買物データ受理
	my @cart = $cgi->param('cart');
	if (@cart == 0) {
        error("買物カゴの中身が空です");
    }

	# 商品データ認識
	my %cart = get_data();

	# 前画面からの戻りの場合
	my %c;
	if ($in{job} eq "back" or %er != 0) {
		%c = %in;

	# 戻りでない場合は顧客情報のクッキー取り出し
	} else {
		my @cust = get_cookie();

		# 復号化
		($c{name},$c{kana},$c{email},$c{zip},$c{pref},$c{addr},$c{tel},$c{fax},$c{name2},$c{kana2},$c{zip2},$c{pref2},$c{addr2},$c{tel2},$c{fax2},$c{deliv}) = decrypt_cust(@cust);
		if ($c{deliv}) { $in{deliv} = $c{deliv}; }
	}

	# 改行復元
	$c{addr}  =~ s/\t/\n/g;
	$c{addr2} =~ s/\t/\n/g;
	$c{memo}  =~ s/\t/\n/g;

	# 送料で有償の地区があるかをチェック
	my ($flg,$remark);
	foreach (0 .. $#{$cf{pref}}) {
		my ($prf,$pri) = split(/,/,${$cf{pref}}[$_]);

		if ($pri > 0) {
			$flg++;
			last;
		}
	}
	if ($flg) { $remark = "(送料等は次画面で計算されます)"; }

	# 支払方法
	my $payment;
	foreach (0 .. $#{$cf{payment}}) {
		my ($pay,$cost) = split(/,/,${$cf{payment}}[$_]);

		if (($in{payment} eq $_) || ($in{payment} eq "" && $_ == 0)) {
			$payment .= qq|<input type="radio" name="payment" value="$_" checked="checked" />$pay<br />\n|;
		} else {
			$payment .= qq|<input type="radio" name="payment" value="$_" />$pay<br />\n|;
		}
	}

	# 配達時間
	my $opt_deli;
	foreach (0 .. $#{$cf{deli}}) {
		if ($in{deli} eq $_) {
			$opt_deli .= qq|<option value="$_" selected="selected">${$cf{deli}}[$_]</option>\n|;
		} else {
			$opt_deli .= qq|<option value="$_">${$cf{deli}}[$_]</option>\n|;
		}
	}

	# 都道府県
	my ($opt_pref,$opt_pref2);
	foreach (0 .. $#{$cf{pref}}) {
		my ($pref,$postage) = split(/,/,${$cf{pref}}[$_]);

		if ($c{pref} eq $_) {
			$opt_pref .= qq|<option value="$_" selected="selected">$pref</option>\n|;
		} else {
			$opt_pref .= qq|<option value="$_">$pref</option>\n|;
		}
		if ($c{pref2} eq $_) {
			$opt_pref2 .= qq|<option value="$_" selected="selected">$pref</option>\n|;
		} else {
			$opt_pref2 .= qq|<option value="$_">$pref</option>\n|;
		}
	}

	# テンプレート読み込み
	open(IN,"$cf{tmpldir}/addr.html") or error("open err: addr.html");
	my $tmpl = join('', <IN>);
	close(IN);
	
    # プログラムファイル名
	$tmpl =~ s/!order_cgi!/$cf{order_cgi}/g;

	# 税対応
	if (!$cf{tax_per}) { $tmpl =~ s/<!-- tax_begin -->.+<!-- tax_end -->//s; }
	
	# 入力エラー
	if (%er != 0) {
		for (qw(name email zip addr tel name2 zip2 addr2 tel2)) {
			if (defined($er{$_})) { $tmpl =~ s|<!-- err:$_ -->|<div class="err-addr">$er{$_}</div>|g; }
		}
	}
	
	# 配送先
	if (!$in{deliv}) { $in{deliv} = 1; }
	$tmpl =~ s|<input type="radio" name="deliv" value="$in{deliv}" ([^>]+)>|<input type="radio" name="deliv" value="$in{deliv}" $1 checked="checked">|g;
	
	# 配送先フォーム
	if ($in{deliv} == 2) {
		$tmpl =~ s/!disp!/block/g;
	} else {
		$tmpl =~ s/!disp!/none/g;
	}
	
	# テンプレート分割
	my ($head,$loop,$foot) = $tmpl =~ /(.+)<!-- item_begin -->(.+)<!-- item_end -->(.+)/s
				? ($1,$2,$3)
				: error("テンプレート不正");

	# 買物カゴ展開
	my $all = 0;
	my ($body,$hidden);
	foreach (@cart) {
		my ($id,$code,$num,@op) = split(/;/);
		my (undef,$name,$price,$memo,$back,@ops) = split(/<>/,$cart{$code});

		# チェック
		$id =~ s/\D//g;
		$code =~ s/\W//g;
		$num  =~ s/\D//g;

		# オプション処理
		my ($memo,@op2);
		foreach my $i (0 .. $#{$cf{options}}) {
			my ($key,$nam) = split(/,/,$cf{options}[$i]);
			$op2[$i] = [split(/\s+/,$ops[$i])];

			if ($op[$i] ne '') { $memo .= "[$nam]$op[$i] "; }
		}

		# 引数
		my $hid = "$id;$code;$num";
		foreach my $i (0 .. $#{$cf{options}}) {
		
			# 正当性チェック
			if ($cf{chk_ops} == 1) {
				my $flg;
				foreach my $opt (@{$op2[$i]}) {
					if ($op[$i] eq $opt) {
						$flg++;
						last;
					}
				}
				if ($op[$i] ne '' && !$flg) { error("属性の値が不正です"); }
			}
			$hid .= ";$op[$i]";
		}

		# 引数定義（次画面用）
		$hidden .= qq|<input type="hidden" name="cart" value="$hid" />\n|;

		# 小計/累計
		my $kei = $price * $num;
		$all += $kei;

		# 書き出し
		my $tmp = $loop;
		$tmp =~ s/!code!/$code/g;
		$tmp =~ s/!item!/$name/g;
		$tmp =~ s/!num!/$num/g;
		$tmp =~ s/!tanka!/comma($price)/ge;
		$tmp =~ s/!gouka!/comma($kei)/ge;
		$tmp =~ s/!memo!/$memo/g;
		$body .= $tmp;
	}

	# 郵便番号Ajax3
	my $zip_ajax3 = $cf{ssl_mode} == 1
		? 'https://ajaxzip3.googlecode.com/svn/trunk/ajaxzip3/ajaxzip3-https.js'
		: 'http://ajaxzip3.googlecode.com/svn/trunk/ajaxzip3/ajaxzip3.js';
	
	# 消費税
	my ($kei,$tax,$all) = tax_per($all);
	
	foreach ($head, $foot) {
		s/!zip_ajax3!/$zip_ajax3/g;
		s/!home!/$cf{home}/g;
		s/!back!/$in{back}/g;
		s/!kei!/comma($kei)/ge;
		s/!tax!/comma($tax)/ge;
		s/!all!/comma($all)/ge;
		s/!remark!/$remark/g;
		s/!payment!/$payment/g;
		s/!mon!/$in{mon}/g;
		s/!day!/$in{day}/g;
		s/!c_(\w+)!/$c{$1}/g;
		s/<!-- option_deli -->/$opt_deli/g;
		s/<!-- option_pref -->/$opt_pref/g;
		s/<!-- option_pref2 -->/$opt_pref2/g;
		s/!renraku!/$c{memo}/g;
		s/<!-- cart -->/$hidden/g;
		s/!([a-z]+_cgi)!/$cf{$1}/g;
}

	# 画面展開
	print "Content-type: text/html; charset=utf-8\n\n";
	print $head, $body;

	# フッタ
	footer($foot);
}

#-----------------------------------------------------------
#  確認画面 (Step2)
#-----------------------------------------------------------
sub conf_form {
	# back属性チェック
	chk_back($in{back});

	# 買物情報取得
	my @cart = $cgi->param('cart');
	if (@cart == 0) { error("買物情報がありません"); }

	# 入力確認
	check_input();

	# 注文者情報をクッキー格納
	my $cookie;
	if ($in{cook} == 1) {
		# 顧客情報暗号化
		my @cust = encrypt_cust($in{name},$in{kana},$in{email},$in{zip},$in{pref},$in{addr},$in{tel},$in{fax},$in{name2},$in{kana2},$in{zip2},$in{pref2},$in{addr2},$in{tel2},$in{fax2},$in{deliv});

		# クッキー保存
		set_cookie(@cust);
	}

	# 在庫認識
	my %zan = get_zan() if ($cf{stock});

	# 商品データ認識
	my %cart = get_data();

	# 都道府県/送料
	my ($pref2,%pref);
	my $postage = 0;
	my ($pref,$postage) = split(/,/,${$cf{pref}}[$in{pref}]);
	$pref{pref} = $pref;
	if ($in{pref2} ne "") {
		($pref2,$postage) = split(/,/,${$cf{pref}}[$in{pref2}]);
		$pref{pref2} = $pref2;
	}

	# 支払方法の手数料
	my ($pay,$cost) = split(/,/,${$cf{payment}}[$in{payment}]);

	# 送料サービスフラグ
	my $serv_flag = 0;

	# 配達時間
	my $deliv;
	if ($in{mon} ne "" && $in{day} ne "") {
		$deliv = "$in{mon}月$in{day}日<br />";
	}
	if ($in{deli} ne "") { $deliv .= ${$cf{deli}}[$in{deli}]; }

	# 郵便番号
	$in{zip}  =~ s/(\d{3})(\d{4})/$1-$2/;
	$in{zip2} =~ s/(\d{3})(\d{4})/$1-$2/;

	# 改行復元
	$in{addr}  =~ s/\t/<br \/>/g;
	$in{addr2} =~ s/\t/<br \/>/g;
	$in{memo}  =~ s/\t/<br \/>/g;

	# テンプレート読み込み
	open(IN,"$cf{tmpldir}/conf.html") or error("open err: conf.html");
	my $tmpl = join('', <IN>);
	close(IN);

	# 税対応
	if (!$cf{tax_per}) { $tmpl =~ s/<!-- tax_begin -->.+<!-- tax_end -->//s; }

	# テンプレート分割
	my ($head,$loop,$foot) = $tmpl =~ /(.+)<!-- item_begin -->(.+)<!-- item_end -->(.+)/s
			? ($1,$2,$3)
			: error("テンプレート不正");

	# 買物カゴ展開
	my $all = 0;
	my $gkei = 0;
	my ($flg,$scode,$body,$hidden);
	foreach (@cart) {
		my ($id,$code,$num,@op) = split(/;/);
		my (undef,$name,$price,$memo,$back,@ops) = split(/<>/,$cart{$code});

		# チェック
		$id =~ s/\D//g;
		$code =~ s/\W//g;
		$num  =~ s/\D//g;

		# オプション処理
		my ($memo,@op2);
		foreach my $i (0 .. $#{$cf{options}}) {
			my ($key,$nam) = split(/,/,$cf{options}[$i]);
			$op2[$i] = [split(/\s+/,$ops[$i])];

			if ($op[$i] ne '') { $memo .= "[$nam]$op[$i] "; }
		}

		# 引数
		my $hid = "$id;$code;$num";
		foreach my $i (0 .. $#{$cf{options}}) {

			# 正当性チェック
			if ($cf{chk_ops} == 1) {
				my $flg;
				foreach my $opt (@{$op2[$i]}) {
					if ($op[$i] eq $opt) {
						$flg++;
						last;
					}
				}
				if ($op[$i] ne '' && !$flg) { error("属性の値が不正です"); }
			}
			$hid .= ";$op[$i]";
		}

		# 引数定義（次画面用）
		$hidden .= qq|<input type="hidden" name="cart" value="$hid" />\n|;

		# 小計/累計
		my $kei = $price * $num;
		$all += $kei;

		# 書き出し
		my $tmp = $loop;
		$tmp =~ s/!code!/$code/g;
		$tmp =~ s/!item!/$name/g;
		$tmp =~ s/!num!/$num/g;
		$tmp =~ s/!tanka!/comma($price)/ge;
		$tmp =~ s/!gouka!/comma($kei)/ge;
		$tmp =~ s/!memo!/$memo/g;
		$body .= $tmp;

		# 在庫数チェック
		if ($cf{stock}) {
			if ($zan{$code} - $num < 0) {
				$scode = $code;
				$flg++;
				last;
			}
		}
	}

	# 在庫切れ
	if ($flg) {
		my ($name) = (split(/<>/,$cart{$scode}))[1];
		my $msg = "大変申し訳ありません。「$name」は在庫切れです(在庫数:$zan{$scode})<br />\n";
		$msg .= "たった今、他の方からの購入があったようです\n";
		error($msg);
	}

	# 送料
	if ($postage > 0) {
		# 送料サービス有り
		if ($cf{cari_serv} && $cf{cari_serv} <= $all) {
			$postage = 0;
			$serv_flag++;
		}
	}

	# 送料が設定されている場合
	if (!$serv_flag) { $all += $postage; }

	# 支払手数料が設定されている場合
	if ($cost > 0) { $all += $cost; }

	# 次画面用パラメータ
	foreach (qw(payment mon day deli name kana email zip pref addr tel fax name2 kana2 zip2 pref2 addr2 tel2 fax2 memo deliv)) {
		my $val = $in{$_};
		if ($_ eq 'addr' or $_ eq 'addr2' or $_ eq 'memo') {
			$val =~ s|<br />|\t|g;
		}
		$hidden .= qq|<input type="hidden" name="$_" value="$val" />\n|;
	}
	
	# 消費税
	my ($kei,$tax,$all) = tax_per($all);
	
	foreach ($head, $foot) {
		s/!home!/$cf{home}/g;
		s/!back!/$in{back}/g;
		s/!kei!/comma($kei)/ge;
		s/!tax!/comma($tax)/ge;
		s/!all!/comma($all)/ge;
		s/!postage!/comma($postage)/ge;
		s/!cost!/comma($cost)/ge;
		s/!c_(\w+)!/$in{$1}/g;
		s/!(pref2?)!/$pref{$1}/g;
		s/!renraku!/$in{memo}/g;
		s/!deliv!/$deliv/g;
		s/!payment!/$pay/g;
		s/<!-- hidden -->/$hidden/g;
		s/!order_cgi!/$cf{order_cgi}/g;
	}

	# 画面展開
	print "Content-type: text/html; charset=utf-8\n\n";
	print $head, $body;

	# フッタ
	footer($foot);
}

#-----------------------------------------------------------
#  注文送信 (Step3)
#-----------------------------------------------------------
sub send_form {
	# 買物情報取得
	my @cart = $cgi->param('cart');
	if (@cart == 0) { error("買物情報がありません"); }

	# 入力確認
	check_input();

	# 改行変換
	for ( keys %in ) {
		if ($_ eq 'addr' or $_ eq 'addr2' or $_ eq 'memo') {
			$in{$_} =~ s/\t+$//;
			$in{$_} =~ s/\t/\n           /g;
		} else {
			$in{$_} =~ s/\t//g;
		}
	}

	# 在庫認識
	my %zan = get_zan() if ($cf{stock});

	# ホスト名/時間を取得
	my $host = get_host();
	my ($date,$mdate) = get_time();
	$in{date} = $date;
	$in{host} = $host;

	# ブラウザ情報
	$in{agent} = $ENV{HTTP_USER_AGENT};
	$in{agent} =~ s/[<>&"']//g;

	# 注文番号採番
	open(DAT,"+< $cf{numfile}") or error("open err: $cf{numfile}");
	eval "flock(DAT, 2);";
	my $num = <DAT>;
	seek(DAT, 0, 0);
	print DAT ++$num;
	truncate(DAT, tell(DAT));
	close(DAT);

	# 桁数調整
	$in{number} = sprintf("%06d", $num);

	# メール件名をMIMEエンコード
	my $msub = Jcode->new("ガットポンポコ ご注文確認 (自動返信メール)",'utf8')->mime_encode;

	# メールヘッダー定義
	my $mhead = <<EOM;
Subject: $msub
Date: $mdate
MIME-Version: 1.0
Content-type: text/plain; charset=ISO-2022-JP
Content-Transfer-Encoding: 7bit
X-Mailer: $cf{version}
EOM

	# データ読み取り
	my %cart = get_data();

	# 買物カゴ展開
	my $all = 0;
	my $i = 0;
	$in{order} = '';
	foreach (@cart) {
		my ($id,$code,$num,@op) = split(/;/);
		my (undef,$name,$price,undef,undef,@ops) = split(/<>/,$cart{$code});

		# チェック
		$id =~ s/\D//g;
		$code =~ s/\W//g;
		$num  =~ s/\D//g;

		# 小計
		my $kei = $price * $num;
		$all += $kei;

		# 在庫チェック
		if ($cf{stock}) {
			if ($zan{$code} - $num < 0) {
				my $msg = "大変申し訳ありません。「$name」は在庫切れです(現在の在庫数:$zan{$code})<br />\n";
				$msg .= "たった今、他の方からの購入があったようです\n";
				error($msg);
			}
			$zan{$code} -= $num;
		}

		# 単価計算
		$price = comma($price);
		$kei   = comma($kei);

		$i++;
		$in{order} .= "●ご注文内容$i\n";
		$in{order} .= "コード : $code\n";
		$in{order} .= "商品名 : $name\n";

		# オプション処理
		my @op2;
		foreach my $i (0 .. $#{$cf{options}}) {
			my ($key,$nam) = split(/,/,$cf{options}[$i]);
			$op2[$i] = [split(/\s+/,$ops[$i])];

			if ($op[$i] ne '') { $in{order} .= "[$nam] $op[$i]\n"; }
		}

		$in{order} .= "金  額 : ￥$price × $num = ￥$kei\n\n";

		# オプション正当チェック
		if ($cf{chk_ops} == 1) {
			foreach my $i (0 .. $#{$cf{options}}) {
				my $flg;
				foreach my $opt (@{$op2[$i]}) {
					if ($op[$i] eq $opt) {
						$flg++;
						last;
					}
				}
				if ($op[$i] ne '' && !$flg) { error("属性の値が不正です"); }
			}
		}
	}
	$in{order} =~ s/\n+$//;

	# 配達時間
	$in{deliv} = '';
	if ($in{mon} ne "" && $in{day} ne "") {
		$in{deliv} = "$in{mon}月$in{day}日";
		if ($in{deli} ne "") {
			$in{deliv} .= " ${$cf{deli}}[$in{deli}]";
		}
	}

	# 都道府県/送料
	my ($pref,$pref2);
	my $postage = 0;
	my ($pref,$postage) = split(/,/,${$cf{pref}}[$in{pref}]);
	$in{pref} = $pref;
	if ($in{pref2} ne "") {
		($pref2,$postage) = split(/,/,${$cf{pref}}[$in{pref2}]);
		$in{pref2} = $pref2;
	}

	# 支払方法の手数料
	my ($pay,$cost) = split(/,/,${cf{payment}}[$in{payment}]);
	my $q_pay = $in{payment};
	$in{payment} = $pay;

	# 県別送料
	my $memo;
	if ($postage > 0) {
		# 送料サービス有り
		$in{postage} = 0;
		if ($cf{cari_serv} && $cf{cari_serv } <= $all) {
			$in{postage} = $postage = 0;
			$in{postage} .= ' (送料サービス)';

		# 送料サービス無し
		} else {
			$all += $postage;
			$in{postage} = comma($postage);
		}
	}
	if ($in{postage} eq '') { $in{postage} = 0; }

	# 支払手数料
	$in{cost} = 0;
	if ($cost > 0) {
		$all += $cost;
		$in{cost} = comma($cost);
	}

	# 消費税
	my ($kei,$tax,$all) = tax_per($all);
	
	# メール本文用
	$in{kei} = comma($kei);
	$in{all} = comma($all);
	$in{tax} = $cf{tax_per} == 0 ? "[内税]" : comma($tax);

	# メール本文テンプレート読出（管理者宛）
	open(IN,"$cf{tmpldir}/order.txt") or error("open err: order.txt");
	my $body_ord = join('', <IN>);
	close(IN);

	# オーダー本文テンプレート読出（注文者宛）
	open(IN,"$cf{tmpldir}/reply.txt") or error("open err: reply.txt");
	my $body_rep = join('', <IN>);
	close(IN);

	# 文字置き換え
	$body_ord =~ s/!(\w+)!/$in{$1}/g;
	$body_rep =~ s/!(\w+)!/$in{$1}/g;

	# ログ用
	my $log = $body_ord;

	# コード変換
	$body_ord = Jcode->new($body_ord,'utf8')->jis;
	$body_rep = Jcode->new($body_rep,'utf8')->jis;

	# タグ復元
	$body_ord = tag_chg($body_ord);
	$body_rep = tag_chg($body_rep);

	# sendmailコマンド定義
	my $scmd1 = "$cf{sendmail} -t -i";
	my $scmd2 = "$cf{sendmail} -t -i";
	if ($cf{sendm_f} == 1) {
		$scmd1 .= qq| -f $in{email}|;
		$scmd2 .= qq| -f $cf{master}|;
	}

	# 管理者へ送信
	open(MAIL,"| $scmd1") or error("メール送信失敗");
	print MAIL "To: $cf{master}\n";
	print MAIL "From: $in{email}\n";
	print MAIL "$mhead\n";
	print MAIL "$body_ord\n";
	close(MAIL);

	# 注文者へ送信
	open(MAIL,"| $scmd2") or error("メール送信失敗");
	print MAIL "To: $in{email}\n";
	print MAIL "From: $cf{master}\n";
	print MAIL "$mhead\n";
	print MAIL "$body_rep\n";
	close(MAIL);

	# 買物情報のクッキー消去
	del_cookie();

	# 在庫数更新
	if ($cf{stock}) {
		my @data;
		while ( my ($id,$zan) = each %zan ) {
			push(@data,"$id<>$zan<>\n");
		}

		open(OUT,"+> $cf{stkfile}") or error("write err: $cf{stkfile}");
		eval "flock(OUT, 2);";
		print OUT @data;
		close(OUT);
	}

	# ログ保存
	save_log($date,$in{number},$log);

	# テンプレート判別
	my $zeus_num;
	my $tmplfile = "send.html";
	# クレジット
	if (($cf{zeus_serv} == 1 && $q_pay == $#{$cf{payment}})
			or ($cf{zeus_serv} == 2 && $q_pay == $#{$cf{payment}}-1)
			or ($cf{zeus_serv} == 3 && $q_pay == $#{$cf{payment}}-1)
			or ($cf{zeus_serv} == 4 && $q_pay == $#{$cf{payment}}-2)) {
		$tmplfile = "send-credit.html";
		$zeus_num = $cf{zeus_num};
		
	# 銀行
	} elsif (($cf{zeus_serv} == 2 && $q_pay == $#{$cf{payment}})
			or ($cf{zeus_serv} == 4 && $q_pay == $#{$cf{payment}}-1)) {
		$tmplfile = "send-bank.html";
		$zeus_num = $cf{zeus_bip};
		
	# コンビニ
	} elsif (($cf{zeus_serv} == 3 && $q_pay == $#{$cf{payment}})
			or ($cf{zeus_serv} == 4 && $q_pay == $#{$cf{payment}})) {
		$tmplfile = "send-conv.html";
		$zeus_num = $cf{zeus_cip};
	}

	# 完了画面
	open(IN,"$cf{tmpldir}/$tmplfile") or error("open err: $tmplfile");
	my $tmpl = join('', <IN>);
	close(IN);

	# 文字置換
	$tmpl =~ s/!home!/$cf{home}/g;

	# ゼウス用
	my $money = $all;
	if ($cf{zeus_serv} > 0) {
		$in{tel} =~ s/\D//g;
		
		$tmpl =~ s/!zeus_num!/$zeus_num/g;
		$tmpl =~ s/!money!/$money/g;
		$tmpl =~ s/!tel!/$in{tel}/g;
		$tmpl =~ s/!email!/$in{email}/g;
		$tmpl =~ s/!sendid!/$in{number}/g;
	}

    # プログラムファイル名
	$tmpl =~ s/!order_cgi!/$cf{order_cgi}/g;

	# 表示
	print "Content-type: text/html; charset=utf-8\n\n";
	footer($tmpl);
}

#-----------------------------------------------------------
#  時間取得
#-----------------------------------------------------------
sub get_time {
	my ($sec,$min,$hour,$mday,$mon,$year,$wday) = (localtime(time))[0..6];

	my @week = qw|Sun Mon Tue Wed Thu Fri Sat|;
	my @mon  = qw|Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec|;

	# 日時フォーマット
	my $date = sprintf("%04d/%02d/%02d(%s) %02d:%02d:%02d",
					$year+1900,$mon+1,$mday,$week[$wday],$hour,$min,$sec);

	# メール用フォーマット
	my $mdate = sprintf("%s, %02d %s %04d %02d:%02d:%02d",
					$week[$wday],$mday,$mon[$mon],$year+1900,$hour,$min,$sec) . " +0900";

	return ($date,$mdate);
}

#-----------------------------------------------------------
#  ホスト名取得
#-----------------------------------------------------------
sub get_host {
	my $host = $ENV{REMOTE_HOST};
	my $addr = $ENV{REMOTE_ADDR};

	if ($cf{gethostbyaddr} && ($host eq "" || $host eq $addr)) {
		$host = gethostbyaddr(pack("C4", split(/\./, $addr)), 2);
	}
	$host ||= $addr;

	return $host;
}

#-----------------------------------------------------------
#  ログ保存
#-----------------------------------------------------------
sub save_log {
	my ($date,$num,$log) = @_;

	# 改行置き換え
	$log =~ s/\n/\t/g;
	$log =~ s/ +/ /g;

	# ログファイル名を定義
	my $file = ($date =~ /^(\d{4})\/(\d{2})/) && "$1$2.cgi";

	# 存在チェック
	my $flg;
	if (-e "$cf{logdir}/$file") { $flg++; }

	# ログ追加書き込み
	open(DAT,">> $cf{logdir}/$file") or error("write err: $file");
	eval "flock(DAT, 2);";
	print DAT "$date<>$num<>$log\n";
	close(DAT);

	# 新規生成の場合はパーミッション付与
	chmod(0666, "$cf{logdir}/$file") if (!$flg);
}

#-----------------------------------------------------------
#  入力チェック
#-----------------------------------------------------------
sub check_input {
	# 改行末尾をカット
	$in{addr}  =~ s/\t+$//g;
	$in{addr2} =~ s/\t+$//g;
	$in{memo}  =~ s/\t+$//g;

	# 入力確認
	my %er;
#	if ($in{payment} eq '') { $er{payment} = '支払方法が未選択です'; }
	if ($in{name} eq '') { $er{name} = '名前が未入力です'; }
	if ($in{email} !~ /^[a-zA-Z0-9.!#$%&'*+=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$/) { $er{email} = '電子メールの入力が不正です'; }
	if ($in{zip} !~ /^\d{3}-?\d{4}$/) { $er{zip} = '郵便番号は「数字7桁」か「数字3桁-4桁」です'; }
	if ($in{pref} eq '' or $in{addr} eq '') { $er{addr} = '住所が未入力です'; }
	if ($in{tel} eq '') { $er{tel} = '電話番号が未入力です'; }
	if ($in{deliv} == 2) {
		if ($in{name2} eq '') { $er{name2} = '配送先の名前が未入力です'; }
		if ($in{zip2} !~ /^\d{3}-?\d{4}$/) { $er{zip2} = '配送先の郵便番号は「数字7桁」か「数字3桁-4桁」です'; }
		if ($in{pref2} eq '' or $in{addr2} eq '') { $er{addr2} = '配送先の住所が未入力です'; }
		if ($in{tel2} eq '') { $er{tel2} = '配送先の電話番号が未入力です'; }
	} else {
		$in{name2} = $in{kana2} = $in{zip2} = $in{addr2} = $in{pref2} = $in{tel2} = $in{fax2} = '';
	}
	if (%er != 0) { addr_form(%er); }
}

#-----------------------------------------------------------
#  タグ復元
#-----------------------------------------------------------
sub tag_chg {
	local($_) = @_;

	s/&lt;/</g;
	s/&gt;/>/g;
	s/&quot;/"/g;
	s/&amp;/&/g;
	$_;
}

#-----------------------------------------------------------
#  顧客情報暗号化
#-----------------------------------------------------------
sub encrypt_cust {
	my @cust = @_;

	my @ret;
	foreach (@cust) {
		my $encrypt = RC4($cf{passphrase}, $_);
		$encrypt =~ s/(.)/unpack('H2', $1)/eg;

		push(@ret,$encrypt);
	}
	return @ret;
}

#-----------------------------------------------------------
#  顧客情報復号化
#-----------------------------------------------------------
sub decrypt_cust {
	my @cust = @_;

	my @ret;
	foreach (@cust) {
		s/([0-9A-Fa-f]{2})/pack('H2', $1)/eg;
		my $decrypt = RC4($cf{passphrase}, $_);
		$decrypt =~ s/[&"'<>]//g;

		push(@ret,$decrypt);
	}
	return @ret;
}

#-----------------------------------------------------------
#  クッキー消去
#-----------------------------------------------------------
sub del_cookie {
	print "Set-Cookie: $cf{cookie_cart}=; expires=Thu, 01-Jan-1970 00:00:00 GMT;\n";
}

#-----------------------------------------------------------
#  クッキー発行
#-----------------------------------------------------------
sub set_cookie {
	my @data = @_;

	my ($sec,$min,$hour,$mday,$mon,$year,$wday,undef,undef) = gmtime(time + 60*24*60*60);
	my @mon  = qw|Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec|;
	my @week = qw|Sun Mon Tue Wed Thu Fri Sat|;

	# 時刻フォーマット
	my $gmt = sprintf("%s, %02d-%s-%04d %02d:%02d:%02d GMT",
				$week[$wday],$mday,$mon[$mon],$year+1900,$hour,$min,$sec);

	# URLエンコード
	my $cook;
	foreach (@data) {
		s/(\W)/sprintf("%%%02X", unpack("C", $1))/eg;
		$cook .= "$_<>";
	}

	print "Set-Cookie: $cf{cookie_cust}=$cook; expires=$gmt;";
	print " secure" if ($cf{ssl_cookie});
	print "\n";
}

#-----------------------------------------------------------
#  クッキー取得
#-----------------------------------------------------------
sub get_cookie {
	# クッキー取得
	my $cook = $ENV{HTTP_COOKIE};

	# 該当IDを取り出す
	my %cook;
	foreach ( split(/;/,$cook) ) {
		my ($key,$val) = split(/=/);
		$key =~ s/\s//g;
		$cook{$key} = $val;
	}

	# URLデコード
	my @cook;
	foreach ( split(/<>/,$cook{$cf{cookie_cust}}) ) {
		s/%([0-9A-Fa-f][0-9A-Fa-f])/pack("H2", $1)/eg;

		push(@cook,$_);
	}
	return @cook;
}

#-----------------------------------------------------------
#  在庫数認識
#-----------------------------------------------------------
sub get_zan {
	my %zan;
	open(IN,"$cf{stkfile}") or error("open err: $cf{stkfile}");
	while (<IN>) {
		my ($id,$zan) = split(/<>/);
		$zan{$id} = $zan;
	}
	close(IN);

	return %zan;
}

