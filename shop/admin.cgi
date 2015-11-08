#!/usr/bin/perl

#┌─────────────────────────────────
#│ WEB MART : admin.cgi - 2014/10/19
#│ copyright (c) KentWeb
#│ http://www.kent-web.com/
#└─────────────────────────────────

# モジュール宣言
use strict;
use CGI::Carp qw(fatalsToBrowser);
use lib "./lib";
use CGI::Minimal;
use Jcode;

# 設定ファイル取り込み
require './init.cgi';
my %cf = set_init();

# データ受理
CGI::Minimal::max_read_size($cf{maxdata});
my $cgi = CGI::Minimal->new;
cgi_err('容量オーバー') if ($cgi->truncated);
my %in = parse_form($cgi);

# 認証
check_passwd();

# 処理分岐
if ($in{data_new}) { data_new(); }
if ($in{data_men}) { data_men(); }
if ($in{look_log}) { look_log(); }
if ($in{data_law}) { data_law(); }
if ($in{data_csv}) { data_csv(); }

# メニュー画面
menu_html();

#-----------------------------------------------------------
#  メニュー画面
#-----------------------------------------------------------
sub menu_html {
	header("メニューTOP |【販売管理】ガットポンポコ");
	print <<EOM;
<div align="center">
<p>選択ボタンを押してください。</p>
<form action="$cf{admin_cgi}" method="post">
<input type="hidden" name="pass" value="$in{pass}">
<table class="form-tbl">
<tr>
	<th>選択</th>
	<th width="280">処理メニュー</th>
</tr><tr>
	<td><input type="submit" name="data_new" value="選択"></td>
	<td>新規商品データ作成</td>
</tr><tr>
	<td><input type="submit" name="data_men" value="選択"></td>
	<td>商品データメンテナンス（修正・削除）</td>
</tr><tr>
	<td><input type="submit" name="data_csv" value="選択"></td>
	<td>CSVダウン/アップロード</td>
</tr><tr>
	<td><input type="submit" name="look_log" value="選択"></td>
	<td>ログデータ閲覧</td>
</tr><tr>
	<td><input type="submit" name="data_law" value="選択"></td>
	<td>特商法ページメンテナンス</td>
</tr><tr>
	<td><input type="button" value="選択" onclick="javascript:window.location='$cf{admin_cgi}'"></td>
	<td>ログアウト</td>
</tr>
</table>
</form>
</div>
</body>
</html>
EOM
	exit;
}

#-----------------------------------------------------------
#  新規記事作成
#-----------------------------------------------------------
sub data_new {
	# コード,商品名,価格,オプション
	my @log = @_;

	# 在庫のとき
	my $zai = shift(@log) if ($cf{stock});

	# 新規商品追加
	if ($in{job} eq "new") { data_add(); }

	# パラメータ指定
	my ($mode,$job,$input_code);
	if ($in{data_new}) {
		$mode = "data_new";
		$job = "new";
		$input_code .= qq|（英数字及びアンダーバーのみ）<br>\n|;
		$input_code .= qq|<input type="text" name="code" size="20">|;
	} else {
		$mode = "data_men";
		$job = "edit2";
		$input_code .= qq|<b>$log[0]</b> （変更不可）\n|;
		$input_code .= qq|<input type="hidden" name="code" value="$log[0]">|;
	}

	# 税表記
	my $tax = $cf{tax_per} == 0 ? $cf{tax_class}[0] : $cf{tax_class}[1];

	header("メニューTOP ＞ 商品登録フォーム |【販売管理】ガットポンポコ");
	back_btn();
	print <<EOM;
<div class="ttl">■ 商品登録フォーム</div>
<blockquote>
<p>
	・ 必要項目を入力して、送信ボタンを押してください。<br>
	・ 「備考」及び「戻り先URL」は検索結果画面で使用。
</p>
<form action="$cf{admin_cgi}" method="post">
<input type="hidden" name="pass" value="$in{pass}">
<input type="hidden" name="$mode" value="1">
<input type="hidden" name="job" value="$job">
<table class="form-tbl items">
<tr>
	<th nowrap>商品コード</th>
	<td>$input_code</td>
</tr><tr>
	<th nowrap>商品名</th>
	<td><input type="text" name="item" size="40" value="$log[1]"></td>
</tr><tr>
	<th nowrap>商品単価</th>
	<td><input type="text" name="price" size="20" value="$log[2]"> 円 &nbsp; [$tax]</td>
</tr>
</table>
<p>以下は検索画面（機能）に必要（検索機能を使用しない場合は入力不要）。</p>
<table class="form-tbl items">
<tr>
EOM

	# 属性情報
	my $i = 4;
	foreach (@{$cf{options}}) {
		$i++;
		my ($key,$nam) = split(/,/);

		print qq|</tr><tr>\n|;
		print qq|<th nowrap>属性指定<br>[$nam]</th>\n|;
		print qq|<td>（複数をスペースで区切る。例：青 赤 黄）<br>\n|;
		print qq|<input type="text" name="op:$key" size="40" value="$log[$i]"></td>|;
	}

	# 在庫管理オプション
	if ($cf{stock}) {
		print qq|</tr><tr>\n|;
		print qq|<th nowrap>在庫数</th>\n|;
		print qq|<td><input type="text" name="zai" size="4" value="$zai"> 個</td>|;
	}

	print <<EOM;
</tr><tr>
	<th nowrap>備考</th>
	<td><input type="text" name="memo" size="40" value="$log[3]"></td>
</tr><tr>
	<th nowrap>戻り先URL</th>
	<td>（http://から記述）<br>
		<input type="text" name="back" size="40" value="$log[4]">
	</td>
</tr>
</table>
<input type="submit" value="送信する">
</form>
</blockquote>
</body>
</html>
EOM
	exit;
}
#-----------------------------------------------------------
#  データ追加
#-----------------------------------------------------------
sub data_add {
	# 入力チェック
	check_input();

	# データ追加
	my ($flg,@log);
	open(DAT,"+< $cf{datfile}") or cgi_err("open err: $cf{datfile}");
	eval "flock(DAT, 2);";
	while(<DAT>) {
		my ($code) = (split(/<>/))[0];

		if ($in{code} eq $code) {
			$flg++;
			last;
		}
		push(@log,$_);
	}

	# コード重複のときはエラー
	if ($flg) {
		close(DAT);
		cgi_err("商品コード（$in{code}）が重複しています");
	}

	# オプション
	my $ops;
	foreach (@{$cf{options}}) {
		my ($key,undef) = split(/,/);

		$ops .= qq|$in{"op:$key"}<>|;
	}

	seek(DAT, 0, 0);
	print DAT @log;
	print DAT "$in{code}<>$in{item}<>$in{price}<>$in{memo}<>$in{back}<>$ops\n";
	truncate(DAT, tell(DAT));
	close(DAT);

	# 在庫数
	if ($cf{stock}) {
		open(DAT,">> $cf{stkfile}") or cgi_err("write err: $cf{stkfile}");
		eval "flock(DAT, 2);";
		print DAT "$in{code}<>$in{zai}<>\n";
		close(DAT);
	}

	# 元画面フォーム
	my $btn = <<EOM;
<form action="$cf{admin_cgi}" method="post">
<input type="hidden" name="data_new" value="1">
<input type="hidden" name="pass" value="$in{pass}">
<input type="submit" value="投稿フォームに戻る" style="width:140px">
</form>
EOM

	# 完了メッセージ
	message("新規商品データを追加しました", $btn);
}

#-----------------------------------------------------------
#  商品データメンテナンス
#-----------------------------------------------------------
sub data_men {
	# 指示フラグ
	my $job = $in{job};

	# --- 修正フォーム
	if ($job eq "edit" && $in{code}) {

		my @log;
		open(IN,"$cf{datfile}") or cgi_err("open err: $cf{datfile}");
		while(<IN>) {
			my @data = split(/<>/);

			if ($in{code} eq $data[0]) {
				chomp(@data);
				@log = @data;
				last;
			}
		}
		close(IN);

		# 在庫ファイル
		if ($cf{stock}) {
			my $zno;
			open(IN,"$cf{stkfile}") or cgi_err("open err: $cf{stkfile}");
			while(<IN>) {
				my ($code,$zan) = split(/<>/);

				if ($in{code} eq $code) {
					$zno = $zan;
					last;
				}
			}
			close(IN);

			unshift(@log,$zno);
		}

		# 修正フォーム
		data_new(@log);

	# --- 修正実行
	} elsif ($job eq "edit2") {

		# 入力チェック
		check_input();

		# 更新データ
		my $new = "$in{code}<>$in{item}<>$in{price}<>$in{memo}<>$in{back}<>";
		foreach (@{$cf{options}}) {
			my ($key,undef) = split(/,/);

			$new .= qq|$in{"op:$key"}<>|;
		}

		# 商品データ修正
		my @log;
		open(DAT,"+< $cf{datfile}") or cgi_err("open err: $cf{datfile}");
		eval "flock(DAT, 2);";
		while(<DAT>) {
			my @data = split(/<>/);

			if ($in{code} eq $data[0]) { $_ = "$new\n"; }
			push(@log,$_);
		}
		seek(DAT, 0, 0);
		print DAT @log;
		truncate(DAT, tell(DAT));
		close(DAT);

		# 在庫更新
		if ($cf{stock}) {
			my ($flg,@log);
			open(DAT,"+< $cf{stkfile}") or cgi_err("open err: $cf{stkfile}");
			eval "flock(DAT, 2);";
			while(<DAT>) {
				my ($code,$zai) = split(/<>/);

				if ($in{code} eq $code) {
					$flg++;
					$_ = "$code<>$in{zai}<>\n";
				}
				push(@log,$_);
			}

			# 新規追加のとき
			if (!$flg) { push(@log,"$in{code}<>$in{zai}<>\n"); }

			seek(DAT, 0, 0);
			print DAT @log;
			truncate(DAT, tell(DAT));
			close(DAT);
		}

	# --- 削除
	} elsif ($job eq "dele" && $in{code}) {

		my @log;
		open(DAT,"+< $cf{datfile}") or cgi_err("open err: $cf{datfile}");
		eval "flock(DAT, 2);";
		while(<DAT>) {
			my ($code) = (split(/<>/))[0];

			next if ($in{code} eq $code);
			push(@log,$_);
		}
		seek(DAT, 0, 0);
		print DAT @log;
		truncate(DAT, tell(DAT));
		close(DAT);

		# 在庫更新
		if ($cf{stock}) {
			my @log;
			open(DAT,"+< $cf{stkfile}") or cgi_err("open err: $cf{stkfile}");
			eval "flock(DAT, 2);";
			while(<DAT>) {
				my ($code,$zai) = split(/<>/);

				next if ($in{code} eq $code);
				push(@log,$_);
			}
			seek(DAT, 0, 0);
			print DAT @log;
			truncate(DAT, tell(DAT));
			close(DAT);
		}
	}

	# 在庫データ認識
	my %zai;
	if ($cf{stock}) {
		open(DAT,"$cf{stkfile}") or cgi_err("open err: $cf{stkfile}");
		while(<DAT>) {
			my ($code,$zai) = split(/<>/);
			$zai{$code} = $zai;
		}
		close(DAT);
	}

	header("メニューTOP ＞ 商品データメンテナンス |【販売管理】ガットポンポコ");
	back_btn();
	print <<EOM;
<div class="ttl">■ 商品データメンテナンス</div>
<blockquote>
<p>処理を選択し、送信ボタンを押してください。</p>
<form action="$cf{admin_cgi}" method="post">
<input type="hidden" name="pass" value="$in{pass}">
<input type="hidden" name="data_men" value="1">
処理：
<select name="job">
<option value="edit">修正
<option value="dele">削除
</select>
<input type="submit" value="送信">
<table class="form-tbl">
<tr>
	<th nowrap>選択</th>
	<th nowrap>商品コード</th>
	<th nowrap>商品名</th>
	<th nowrap>金額</th>
EOM

	print qq|<th nowrap>在庫</th>| if ($cf{stock});
	print qq|</tr>\n|;

	open(IN,"$cf{datfile}") or cgi_err("open err: $cf{datfile}");
	while(<IN>) {
		my ($code,$item,$price,$memo,$back,@op) = split(/<>/);
		$price = comma($price);

		print qq|<tr><td class="ta-c"><input type="radio" name="code" value="$code"></td>|;
		print qq|<td nowrap>$code</td>|;
		print qq|<td nowrap>$item</td>|;
		print qq|<td nowrap class="ta-r">￥$price</td>|;
		print qq|<td nowrap class="ta-r">$zai{$code}<br></td>| if ($cf{stock});
		print qq|</tr>\n|;
	}
	close(IN);

	print <<EOM;
</table>
</form>
</blockquote>
</body>
</html>
EOM
	exit;
}

#-----------------------------------------------------------
#  ログデータ閲覧
#-----------------------------------------------------------
sub look_log {
	# 閲覧ボタン確認
	my $look;
	foreach ( keys %in ) {
		if (/^look:(\d+)$/) {
			$look = $1;
			last;
		}
	}
	# 個別閲覧
	if ($look) { look_num($look); }

	# 年月データ
	my $q_ym = $in{ym};

	# 入力内容が規定外の場合は現在の年月
	if ($q_ym !~ /^\d{6}$/) {
		my ($m,$y) = (localtime())[4,5];
		$q_ym = sprintf("%04d%02d", $y+1900,$m+1);
	}

	header("メニューTOP ＞ ログデータ閲覧 |【販売管理】ガットポンポコ");
	back_btn();
	print <<EOM;
<div class="ttl">■ ログデータ閲覧</div>
<blockquote>
<p>年月を切り替えて閲覧することができます。</p>
<form action="$cf{admin_cgi}" method="post">
<input type="hidden" name="pass" value="$in{pass}">
<input type="hidden" name="look_log" value="1">
年月：
<select name="ym">
EOM

	opendir(DIR,"$cf{logdir}") or cgi_err("open err: $cf{logdir}");
	while( $_ = readdir(DIR) ) {

		if (/^(\d{4})(\d{2})\.cgi$/) {
			if ($q_ym == "$1$2") {
				print qq|<option value="$1$2" selected>$1年$2月\n|;
			} else {
				print qq|<option value="$1$2">$1年$2月\n|;
			}
		}
	}
	closedir(DIR);

	print <<EOM;
</select>
<input type="submit" value="切替">
<table class="form-tbl">
<tr>
	<th nowrap>選択</th>
	<th nowrap>注文日時</th>
	<th nowrap>注文番号</th>
</tr>
EOM

	open(IN,"$cf{logdir}/$q_ym.cgi");
	while(<IN>) {
		my ($date,$num,$log) = split(/<>/);

		print qq|<tr><td><input type="submit" name="look:$num" value="閲覧"></td>\n|;
		print qq|<td nowrap>$date</td>\n|;
		print qq|<td nowrap class="ta-c">$num</td></tr>\n|;
	}
	close(IN);

	print <<EOM;
</table>
</form>
</blockquote>
</body>
</html>
EOM
	exit;
}

#-----------------------------------------------------------
#  個別ログ閲覧
#-----------------------------------------------------------
sub look_num {
	my $look = shift;

	# ログデータ名
	my $log = ($in{ym} =~ /^(\d{4})(\d{2})$/) && "$1$2.cgi";

	# ログオープン
	my $data;
	open(IN,"$cf{logdir}/$log") or cgi_err("open err: $log");
	while(<IN>) {
		my ($date,$num,$body) = split(/<>/);

		if ($look == $num) {
			$data = $_;
			last;
		}
	}
	close(IN);

	my ($date,$num,$body) = split(/<>/,$data);
	$body =~ s/\t/<br>/g;

	header("メニューTOP ＞ ログデータ閲覧 ＞ 個別ログ |【販売管理】ガットポンポコ");
	back_btn('look_log');
	print <<EOM;
<div class="ttl">■ ログデータ閲覧 ＞ 個別ログ</div>
<p>
	・注文年月： <b>$date</b><br>
	・注文番号： <b>$num</b><br>
</p>
$body
</body>
</html>
EOM
	exit;
}

#-----------------------------------------------------------
#  特商法メンテ
#-----------------------------------------------------------
sub data_law {
	# 更新
	if ($in{submit}) {

		# 改行変換
		$in{law_text} =~ s/\t/\n/g;

		# 上書き
		open(DAT,"+> $cf{lawfile}") or cgi_err("write err: $cf{lawfile}");
		print DAT $in{law_text};
		close(DAT);

		message("特商法を更新しました");
	}

	# データ読み取り
	open(IN,"$cf{lawfile}") or cgi_err("open err: $cf{lawfile}");
	my $data = join('', <IN>);
	close(IN);

	header("メニューTOP ＞ 特商法メンテナンス |【販売管理】ガットポンポコ");
	back_btn();
	print <<EOM;
<div class="ttl">■ 特商法メンテナンス</div>
<blockquote>
<p>変更内容を修正し、送信ボタンを押してください。</p>
<form action="$cf{admin_cgi}" method="post">
<input type="hidden" name="pass" value="$in{pass}">
<input type="hidden" name="data_law" value="1">
<textarea name="law_text" cols="72" rows="20">$data</textarea>
<br><br>
<input type="submit" name="submit" value="送信する" style="width:100px">
</form>
</blockquote>
</body>
</html>
EOM
	exit;
}

#-----------------------------------------------------------
#  CSVダウン/アップロード
#-----------------------------------------------------------
sub data_csv {
	# ダウンロード
	if ($in{downld}) {

		# Jcode宣言
		my $j = new Jcode;

		open(DAT,"$cf{datfile}") or error("open err: $cf{datfile}");

		# ダウンロード用ヘッダ
		print "Content-type: application/octet-stream\n";
		print "Content-Disposition: attachment; filename=data.csv\n\n";

		# バイナリ出力 (Windowsサーバ環境)
		binmode(STDOUT);

		while ( my $log = <DAT> ) {
			chomp($log);
			$log = $j->set(\$log,'utf8')->sjis;

			my $csv;
			foreach ( split(/<>/,$log) ) {
				$csv .= "$_,";
			}
			print "$csv\r\n";
		}
		close(DAT);
		exit;

	# アップロード
	} elsif ($in{upload} && $in{upfile}) {

		# Jcode宣言
		#my $j = new Jcode;

		# ファイル名
		my $fname = $cgi->param_filename("upfile");
		if ($fname !~ /\.csv$/i) { error('CSVファイルのみアップロードできます。'); }

		my @log;
		foreach my $log ( split(/\r\n|\r|\n/, $in{upfile}) ) {
			#$log = $j->set(\$log,'sjis')->utf8;

			my $csv;
			foreach ( split(/,/,$log) ) {
				$csv .= "$_<>";
			}
			push(@log,"$csv\n");
		}

		# 上書き
		open(DAT,"+> $cf{datfile}") or error("write err: $cf{datfile}");
		print DAT @log;
		close(DAT);

		message('CSVをアップ更新しました');
	}

	header("メニューTOP ＞ CSVダウン/アップロード |【販売管理】ガットポンポコ");
	back_btn();
	print <<EOM;
<div class="ttl">■ CSVダウン/アップロード</div>
<blockquote>
<p>商品データをCSV形式でダウンロードすることができます。</p>
<form action="$cf{admin_cgi}" method="post" enctype="multipart/form-data">
<input type="hidden" name="pass" value="$in{pass}">
<input type="hidden" name="data_csv" value="1">
<table class="form-tbl">
<tr>
	<th>CSVダウンロード</th>
	<td><input type="submit" name="downld" value="ダウンロード"></td>
</tr>
</table>
<p>商品データをCSV形式でアップロードすることができます。</p>
<table class="form-tbl">
<tr>
	<th>CSVアップロード</th>
	<td>
		<input type="file" name="upfile" size="32"><br>
		<input type="submit" name="upload" value="アップロード">
	</td>
</tr>
</table>
<p>
	【参考】CSVフォーマット<br>
	<span style="letter-spacing:1px;color:red">商品コード,商品名,単価,備考,戻り先,属性情報1,属性情報2, ... [改行]</span><br>
	↑上記で、属性情報とは「サイズ,カラー」等で、init.cgiで指定する\$cf{options}の個数分が続く。<br>
	（例）属性情報が「サイズ,カラー」であれば、<span style="letter-spacing:1px;color:red">商品コード,商品名,単価,備考,戻り先,サイズ,カラー [改行]</span>
</p>
</form>
</blockquote>
</body>
</html>
EOM
	exit;
}

#-----------------------------------------------------------
#  入力チェック
#-----------------------------------------------------------
sub check_input {
	# 禁止文字排除
	$in{code}  =~ s/\W//g;
	$in{price} =~ s/\D//g;

	# 在庫のとき
	if ($cf{stock}) {
		$in{zai} =~ s/\D//g;
		if ($in{zai} eq "") { $in{zai} = 0; }
	}

	# 入力チェック
	my $err;
	if ($in{code} eq "") { $err .= "商品コードが未入力です<br>"; }
	if ($in{item} eq "") { $err .= "商品名が未入力です<br>"; }
	if ($in{price} eq "") { $err .= "商品単価が未入力です<br>"; }
	if ($err) { cgi_err($err); }
}

#-----------------------------------------------------------
#  パスワード認証
#-----------------------------------------------------------
sub check_passwd {
	# パスワードが未入力の場合は入力フォーム画面
	if ($in{pass} eq "") {
		enter_form();

	# パスワード認証
	} elsif ($in{pass} ne $cf{password}) {
		cgi_err("認証できません");
	}
}

#-----------------------------------------------------------
#  入室画面
#-----------------------------------------------------------
sub enter_form {
	header("入室画面 |【販売管理】ガットポンポコ");
	print <<EOM;
<form action="$cf{admin_cgi}" method="post">
<div class="enter-form">
	<fieldset><legend>管理パスワード入力</legend><br>
	<input type="password" name="pass" size="25">
	<input type="submit" value=" 認証 "><br><br>
	</fieldset>
</div>
</form>
<script language="javascript">
<!--
self.document.forms[0].pass.focus();
//-->
</script>
</body>
</html>
EOM
	exit;
}

#-----------------------------------------------------------
#  HTMLヘッダー
#-----------------------------------------------------------
sub header {
	my $ttl = shift;

	print <<EOM;
Content-type: text/html; charset=utf-8

<html>
<head>
<meta http-equiv="content-type" content="text/html; charset=utf-8">
<meta http-equiv="content-style-type" content="text/css">
<style type="text/css">
<!--
body,td,th { font-size:80%; background:#f0f0f0; font-family: Verdana,"MS PGothic","Osaka",Arial,sans-serif; width:50%;margin-left: auto; margin-right: auto; }
table.form-tbl { border-collapse:collapse; margin:1em 0; }
table.form-tbl th, table.form-tbl td { border:1px solid #8080c0; padding:6px; }
table.form-tbl th { background:#dcdced; }
table.form-tbl td { background:#fff; }
div.ttl { border-bottom:1px solid #003a75; color:#003a75; padding:4px; font-weight:bold; }
div.enter-form { width:30em; margin:3em auto; text-align:center; }
.ta-c { text-align:center; }
.ta-r { text-align:right; }
table.items th { width:100px; }
table.items td { width:300px; }
-->
</style>
<title>$ttl</title>
</head>
<body>
EOM
}

#-----------------------------------------------------------
#  戻りボタン
#-----------------------------------------------------------
sub back_btn {
	my $mode = shift;

	print <<EOM;
<div align="right">
<form action="$cf{admin_cgi}" method="post">
<input type="hidden" name="pass" value="$in{pass}">
@{[ $mode ? qq|<input type="submit" name="$mode" value="&lt; 前画面">| : "" ]}
<input type="submit" value="&lt; メニュー">
</form>
</div>
EOM
}

#-----------------------------------------------------------
#  エラー
#-----------------------------------------------------------
sub cgi_err {
	my $msg = shift;

	header("ERROR! |【販売管理】ガットポンポコ");
	print <<EOM;
<div class="ta-c">
<hr width="350">
<h3>ERROR!</h3>
<p style="color:#dd0000">$msg</p>
<hr width="350">
<input type="button" value="前画面に戻る" onclick="history.back()">
</div>
</body>
</html>
EOM
	exit;
}

#-----------------------------------------------------------
#  メッセージ表示
#-----------------------------------------------------------
sub message {
	my ($msg,$btn) = @_;

	header("処理完了 |【販売管理】ガットポンポコ");
	print <<EOM;
<div class="ttl">■ 処理完了</div>
<blockquote>
<p style="color:#008000">$msg</p>
$btn
<form action="$cf{admin_cgi}" method="post">
<input type="hidden" name="pass" value="$in{pass}">
<input type="submit" value="メニューに戻る" style="width:140px">
</form>
</blockquote>
</body>
</html>
EOM
	exit;
}


