#!/usr/bin/perl

#┌─────────────────────────────────
#│ WEB MART : mart.cgi - 2014/10/19
#│ copyright (c) KentWeb
#│ http://www.kent-web.com/
#└─────────────────────────────────

# モジュール宣言
use strict;
use CGI::Carp qw(fatalsToBrowser);
use lib "./lib";
use CGI::Minimal;

# 外部ファイル取り込み
require './init.cgi';
my %cf = set_init();

# データ受理
CGI::Minimal::max_read_size($cf{maxdata});
my $cgi = CGI::Minimal->new;
cgi_err('容量オーバー') if ($cgi->truncated);
my %in = parse_form($cgi);

# 処理分岐
if ($in{mode} eq "law") { law_data(); }
if ($in{mode} eq "chg") { chg_cart(); }
pick_cart();

#-----------------------------------------------------------
#  カゴ入れ
#-----------------------------------------------------------
sub pick_cart {
	# コード/数量の正当性
	$in{code} =~ s/\W//g;
	$in{num}  =~ s/\D//g;

	# BACK属性がなければ、HTTP_REFERERで取得
	$in{back} ||= $ENV{HTTP_REFERER};
	if ($in{back}) {
		chk_back($in{back});
	} else {
		error("BACK属性がありません");
	}

	# 登録データ認識
	my %cart = get_data();

	# 個数がない場合は1とする
	if ($in{num} eq '') { $in{num} = 1; }

	# コードがない場合は「中身確認」
	if ($in{code} eq '') {
		my @cook = get_cookie();
		basket(\@cook,\%cart);
	}

	# 商品コードの整合性チェック
	error("商品コード「$in{code}」は未登録です") if (!defined($cart{$in{code}}));

	# 在庫管理の場合
	chk_stock($in{code},$in{num}) if ($cf{stock});

	# クッキー取得
	my @cook = get_cookie();

	# 重複チェック
	my ($flg,@new);
	foreach (@cook) {
		my ($id,$code,$num,@op) = split(/,/);

		if ($in{code} eq $code) {
			my $chk;
			foreach my $i (0 .. $#{$cf{options}}) {
				my ($key,$nam) = split(/,/,$cf{options}[$i]);

				if ($op[$i] ne $in{$key}) {
					$chk++;
					last;
				}
			}
			# 要素が同じ場合は数量を足しこむ（重複する場合）
			if (!$chk) {
				$flg++;
				$num += $in{num};
				$_ = "$id,$code,$num";
				foreach my $op (@op) {
					$_ .= ",$op";
				}
			}
		}
		push(@new,$_);
	}
	@cook = @new;

	# 重複がなければ買物カゴへ追加
	if (!$flg) {

		# 商品情報
		my (undef,undef,undef,undef,undef,@ops) = split(/<>/,$cart{$in{code}});

		# オプションを二次元配列化
		my $i = 0;
		my @op;
		foreach (0 .. $#{$cf{options}}) {
			$op[$i] = [split(/\s+/,$ops[$_])];
			$i++;
		}

		# ID番号発行
		my ($id) = (split(/,/,$cook[0]))[0];
		$id++;

		# 追加分
		my $add = "$id,$in{code},$in{num}";

		# オプション
		foreach my $i (0 .. $#{$cf{options}}) {
			my ($key,$nam) = split(/,/,$cf{options}[$i]);

			# 正当性をチェック
			if ($in{$key} ne '' && $cf{chk_ops} == 1) {
				my $flg;
				foreach (@{$op[$_]}) {
					if ($_ eq $in{$key}) {
						$flg++;
						last;
					}
				}
				if (!$flg) {
					my $msg = qq|$in{$key}は不正な値です|;
					error($msg);
				}
			}
			$add .= qq|,$in{$key}|;
		}
		unshift(@cook,$add);
	}

	# クッキー格納
	set_cookie(@cook);

	# カゴ確認画面
	basket(\@cook,\%cart);
}

#-----------------------------------------------------------
#  買物カゴ画面表示
#-----------------------------------------------------------
sub basket {
	my ($cook,$mart) = @_;

	# テンプレート読み込み
	open(IN,"$cf{tmpldir}/mart.html") or error("open err: mart.html");
	my $tmpl = join('', <IN>);
	close(IN);
	
	# 税対応
	if (!$cf{tax_per}) { $tmpl =~ s/<!-- tax_begin -->.+<!-- tax_end -->//s; }
	
	# テンプレート分解
	my ($head,$loop,$foot) = $tmpl =~ /(.+)<!-- item_begin -->(.+)<!-- item_end -->(.+)/s
			? ($1,$2,$3)
			: error("テンプレート不正");

	# 商品内容を展開
	my $all = 0;
	my ($body,$cart);
	foreach my $ck (@{$cook}) {
		my ($id,$code,$num,@op) = split(/,/,$ck);
		my (undef,$name,$price,$memo,$back,@ops) = split(/<>/,$mart->{$code});

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
		$cart .= qq|<input type="hidden" name="cart" value="$hid" />\n|;

		# 小計/累計
		my $kei = $price * $num;
		$all += $kei;

		# プルダウン生成
		my ($sel_num,$flg);
		foreach my $i (1 .. $cf{max_select}) {
			if ($num == $i) {
				$flg++;
				$sel_num .= qq|<option value="$i" selected="selected">$i</option>\n|;
			} else {
				$sel_num .= qq|<option value="$i">$i</option>\n|;
			}
		}
		if (!$flg) { $sel_num .= qq|<option value="$num" selected="selected">$num</option>\n|; }

		my $tmp = $loop;
		$tmp =~ s/!code!/$code/g;
		$tmp =~ s/!item!/$name/g;
		$tmp =~ s/!num!/num:$id/g;
		$tmp =~ s/<!-- sel_num -->/$sel_num/g;
		$tmp =~ s/!chg!/chg:$id/g;
		$tmp =~ s/!tanka!/comma($price)/ge;
		$tmp =~ s/!gouka!/comma($kei)/ge;
		$tmp =~ s/!del!/del:$id/g;
		$tmp =~ s/!memo!/$memo/g;
		
		$body .= $tmp;
	}
	
	# 消費税
	my ($kei,$tax,$all) = tax_per($all);
	
	# 文字置換
	foreach ($head,$foot) {
		s/!back!/$in{back}/g;
		s/!kei!/comma($kei)/ge;
		s/!tax!/comma($tax)/ge;
		s/!all!/comma($all)/ge;
		s/<!-- cart -->/$cart/g;
		s/!home!/$cf{home}/g;
		s/!([a-z]+_cgi)!/$cf{$1}/g;
	}

	# 画面表示
	print "Content-type: text/html; charset=utf-8\n\n";
	print $head, $body;

	# フッタ
	footer($foot);
}

#-----------------------------------------------------------
#  カート内容変更
#-----------------------------------------------------------
sub chg_cart {
	# 商品コード
	$in{code} =~ s/\W//g;

	# 変更/削除ボタン認識
	my ($chg_num,$del_num);
	foreach ( keys %in ) {
		if (/^chg:(\d+)/) {
			$chg_num = $1;
			last;
		} elsif (/^del:(\d+)/) {
			$del_num = $1;
			last;
		}
	}

	# クッキー取得
	my @get = get_cookie();

	my ($mycode,$mynum,@cook);
	foreach (@get) {
		my ($id,$code,$num,@op) = split(/,/);

		# 変更
		if ($chg_num eq $id) {
			$mycode = $code;
			$mynum  = $in{"num:$id"};
			$_ = qq|$id,$code,$in{"num:$id"}|;
			foreach my $op (@op) {
				$_ .= ",$op";
			}

		# 削除
		} elsif ($del_num eq $id) {
			next;
		}
		push(@cook,$_);
	}

	# 数量変更の場合、在庫チェック
	if ($cf{stock} && $chg_num) { chk_stock($mycode,$mynum); }

	# クッキー格納
	set_cookie(@cook);

	# 買物カゴ
	my %cart = get_data();
	basket(\@cook,\%cart);
}

#-----------------------------------------------------------
#  数字半角変換
#-----------------------------------------------------------
sub num_z2h {
	local($_) = @_;

	s/０/0/g;
	s/１/1/g;
	s/２/2/g;
	s/３/3/g;
	s/４/4/g;
	s/５/5/g;
	s/６/6/g;
	s/７/7/g;
	s/８/8/g;
	s/９/9/g;
	$_;
}

#-----------------------------------------------------------
#  在庫数チェック
#-----------------------------------------------------------
sub chk_stock {
	my ($qcode,$qnum) = @_;

	my ($flg,$zaiko);
	open(IN,"$cf{stkfile}") or error("open err: $cf{stkfile}");
	while (<IN>) {
		my ($code,$zan) = split(/<>/);

		if ($qcode eq $code) {
			if ($zan - $qnum < 0) {
				$zaiko = $zan;
				$flg++;
				last;
			}
		}
	}
	close(IN);

	# 在庫なし
	error("誠に申し訳ありません。<br />この商品は在庫切れです(在庫数:<b>$zaiko</b>)") if ($flg);
}

#-----------------------------------------------------------
#  クッキー取得
#-----------------------------------------------------------
sub get_cookie {
	# クッキー取得
	$ENV{HTTP_COOKIE} =~ /$cf{cookie_cart}=([^=;]+);?/;
	my $cook = $1;
	$cook =~ s/\s//g;

	# URLデコード
	my @cook;
	foreach ( split(/<>/,$cook) ) {
		s/%([0-9A-Fa-f][0-9A-Fa-f])/pack("H2",$1)/eg;
		s/[&"'<>]//g;

		push(@cook,$_);
	}
	return @cook;
}

#-----------------------------------------------------------
#  クッキー発行
#-----------------------------------------------------------
sub set_cookie {
	my @data = @_;

	# URLエンコード
	my $cook;
	foreach (@data) {
		s/(\W)/sprintf("%%%02X", unpack("C", $1))/eg;
		$cook .= "$_<>";
	}

	print "Set-Cookie: $cf{cookie_cart}=$cook\n";
}

