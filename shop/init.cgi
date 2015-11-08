# モジュール宣言/変数初期化
use strict;
my %cf;
#┌─────────────────────────────────
#│ WEB MART : init.cgi - 2014/10/19
#│ copyright (c) KentWeb
#│ http://www.kent-web.com/
#└─────────────────────────────────
$cf{version} = 'Web Mart v5.0';
#┌─────────────────────────────────
#│ [注意事項]
#│ 1. このプログラムはフリーソフトです。このプログラムを使用した
#│    いかなる損害に対して作者は一切の責任を負いません。
#│ 2. 設置に関する質問はサポート掲示板にお願いいたします。
#│    直接メールによる質問は一切お受けいたしておりません。
#└─────────────────────────────────

#===========================================================
# ■ 基本設定
#===========================================================

# 管理用パスワード
$cf{password} = '012345678q';

# 消費税方式
# 0     : 内税方式
# 0以外 : 外税方式にて%単位で指定
$cf{tax_per} = 0;

# 暗号化キー（適当な英数字を指定）
# → 注文者情報をクッキー保存する際の暗号化キー
$cf{passphrase} = "passphrase";

# SSL領域での設置
# 0 : なし
# 1 : あり
$cf{ssl_mode} = 1;

# 管理者アドレス
$cf{master} = 'noen@kobapan.com';

# sendmailパス【サーバパス】
$cf{sendmail} = '/usr/sbin/sendmail';

# sendmailの -fオプション (0=no 1=yes)
# → サーバ仕様として必要な場合
$cf{sendm_f} = 0;

# 買物プログラムURL 【URLパス】
$cf{mart_cgi} = 'https://kurakazuki.sakura.ne.jp/shop/';

# 注文プログラムURL【URLパス】
$cf{order_cgi} = 'https://kurakazuki.sakura.ne.jp/shop/order.cgi';

# 検索プログラムURL【URLパス】
$cf{find_cgi} = './find.cgi';

# 管理プログラムURL 【URLパス】
$cf{admin_cgi} = './admin.cgi';

# データファイル【サーバパス】
$cf{datfile} = './data/mart.dat';

# 注文番号ファイル【サーバパス】
$cf{numfile} = './data/num.dat';

# 特商法データファイル【サーバパス】
$cf{lawfile} = './data/law.txt';

# ログディレクトリ【サーバパス】
$cf{logdir} = './data/log';

# 在庫管理を行う (0=no 1=yes)
$cf{stock} = 1;

# 在庫ファイル【サーバパス】
$cf{stkfile} = './data/stock.dat';

# テンプレートディレクトリ【サーバパス】
$cf{tmpldir} = "./tmpl";

# クッキー（顧客情報）をSSL対応 (0=no 1=yes)
# → SSL配下でクッキー（顧客情報）を使う場合secure属性を付加
$cf{ssl_cookie} = 0;

# 戻り先URL【URLパス】
$cf{home} = "https://kurakazuki.sakura.ne.jp/shop/";

# 都道府県
# → 県別に送料を指定する時はコンマの後に送料を指定
# → 送料が不要な場合は送料部分を 0 とする
$cf{pref} = [
	'',
	'北海道,1028',
	'青森県,720',
	'秋田県,720',
	'岩手県,720',
	'山形県,720',
	'宮城県,720',
	'福島県,720',
	'群馬県,514',
	'栃木県,514',
	'山梨県,514',
	'茨城県,514',
	'千葉県,514',
	'埼玉県,514',
	'東京都,514',
	'神奈川県,514',
	'新潟県,514',
	'長野県,514',
	'静岡県,514',
	'愛知県,514',
	'岐阜県,514',
	'三重県,514',
	'石川県,411',
	'富山県,514',
	'福井県,514',
	'滋賀県,514',
	'京都府,514',
	'大阪府,514',
	'奈良県,514',
	'兵庫県,514',
	'和歌山県,514',
	'島根県,617',
	'鳥取県,617',
	'山口県,617',
	'広島県,617',
	'岡山県,617',
	'愛媛県,720',
	'香川県,720',
	'高知県,720',
	'徳島県,720',
	'福岡県,720',
	'佐賀県,720',
	'長崎県,720',
	'熊本県,720',
	'大分県,720',
	'宮崎県,720',
	'鹿児島県,720',
	'沖縄県,1542',
	];

# 送料の無料サービスの合計金額
# → 一定金額以上の場合に送料を無料
# → この機能を使用しない場合は 0 にする
$cf{cari_serv} = 0;

# 支払方法の指定（複数指定可）
# → 支払い別に手数料を指定する時はコンマの後に送料を指定
# → 手数料が不要な場合は手数料部分を 0 とする
$cf{payment} = [
		'銀行振込,0',
		'郵便振替,0',
		'代金引換,525',
	];

# 支払手数料は税込み (0=no 1=yes)
$cf{paym_tax} = 1;

# 配達時間の選択
$cf{deli} = ['午前中', '12-14時', '14-16時', '16-18時', '18-20時', '20-21時'];

# 商品の属性情報（複数指定可）
# → 買物カゴで指定するname値とその呼称をコンマで区切る
# → name値は英数字、アンダーのみ使用可
$cf{options} = [
		'color,カラー',
		'size,サイズ',
	];

# 外税・内税の表記（検索画面）
# → 順に、内税、外税
$cf{tax_class} = ['税込み', '税別'];

# 商品の属性情報の正当性をチェックする
# → 管理画面で入力する属性情報の正当性を、購入時にチェックする
# → 0=no 1=yes
$cf{chk_ops} = 0;

# クッキーID
# → 順に、買物データ、住所氏名情報、検索時戻り先
$cf{cookie_cart} = 'wmart_cart';
$cf{cookie_cust} = 'wmart_cust';
$cf{cookie_find} = 'wmart_find';

# ホスト取得方法
# 0 : gethostbyaddr関数を使わない
# 1 : gethostbyaddr関数を使う
$cf{gethostbyaddr} = 0;

# 管理画面のページ当り商品表示件数
$cf{pageLog} = 20;

# 買物カゴの中身画面での数量調節の範囲（プルダウン式）
# → 必ず 1 以上の値にすること
$cf{max_select} = 10;

# １度の投稿で受理できる最大サイズ (bytes)
# → 1024Byte = 100KB
$cf{maxdata} = 307200;

# --- [ ここより下は検索画面の設定 ]

# 検索結果の一画面表示数
$cf{pg_max} = 10;

# 画像ファイルの拡張子
# → ドットは書かない
$cf{img_ext} = 'jpg';

# 画像ファイルのディレクトリ
# → 順に、サーバパス、URLパス
$cf{imgdir} = "./img";
$cf{imgurl} = "./img";

# --- [ ここより下はゼウス (ZEUS) クレジット決済の設定 ]
#
# [ ゼウスサービスを利用する ]
#  0 : しない
#  1 : クレジット利用【ゼウス社との契約必要】
#  2 : クレジット＋銀行決済サービスを利用【ゼウス社との契約必要】
#  3 : クレジット＋コンビニ決済サービスを利用【ゼウス社との契約必要】
#  4 : クレジット＋銀行決済＋コンビニ決済サービスを利用【ゼウス社との契約必要】
$cf{zeus_serv} = 0;

# ゼウス契約NO (クレジット決済用IPコード) 
# → $cf{zeus_serv} が 1, 2, 3, 4 の場合必須
$cf{zeus_num} = '11111';

# ゼウス契約NO (銀行決済用IPコード) 
# → $cf{zeus_serv} が 2, 4 の場合必須
$cf{zeus_bip} = '22222';

# ゼウス契約NO (コンビニ決済用IPコード) 
# → $cf{zeus_serv} が 3, 4 の場合必須
$cf{zeus_cip} = '33333';

#===========================================================
# ■ 設定完了
#===========================================================

# 再定義
if ($cf{zeus_serv} >= 1) { push(@{$cf{payment}},"クレジット [連携して決済します],0"); }
if ($cf{zeus_serv} == 2 or $cf{zeus_serv} == 4) { push(@{$cf{payment}},"銀行決済 [連携して決済します],0"); }
if ($cf{zeus_serv} >= 3) { push(@{$cf{payment}},"コンビニ決済 [連携して決済します],0"); }

# 設定内容を返す
sub set_init {
	return %cf;
}

#-----------------------------------------------------------
#  フォームデコード
#-----------------------------------------------------------
sub parse_form {
	my $cgi = shift;

	my %in;
	foreach ( $cgi->param() ) {
		my $val = $cgi->param($_);

		if ($_ ne 'upfile') {
			# 変換
			$val =~ s/&/&amp;/g;
			$val =~ s/</&lt;/g;
			$val =~ s/>/&gt;/g;
			$val =~ s/"/&quot;/g;
			$val =~ s/'/&#39;/g;
			$val =~ s/－/-/g;
			$val =~ s/～/~/g;
			$val =~ s/\r\n/\t/g;
			$val =~ s/[\r\n]/\t/g;
		}
		$in{$_} = $val;
	}
	return %in;
}

#-----------------------------------------------------------
#  特定商取引法
#-----------------------------------------------------------
sub law_data {
	open(IN,"$cf{lawfile}") or error("open err: $cf{lawfile}");
	my $log = join('', <IN>);
	close(IN);

	open(IN,"$cf{tmpldir}/law.html") or error("open err: law.html");
	my $tmpl = join('', <IN>);
	close(IN);

	$tmpl =~ s/!law_data!/$log/;

	print "Content-type: text/html; charset=utf-8\n\n";
	print $tmpl;
	exit;
}

#-----------------------------------------------------------
#  エラー処理
#-----------------------------------------------------------
sub error {
	my $msg = shift;

	open(IN,"$cf{tmpldir}/error.html") or die;
	my $tmpl = join('', <IN>);
	close(IN);

	$tmpl =~ s/!message!/$msg/g;

	print "Content-type: text/html; charset=utf-8\n\n";
	print $tmpl;
	exit;
}

#-----------------------------------------------------------
#  フッター
#-----------------------------------------------------------
sub footer {
	my $foot = shift;

	if ($foot =~ /(.+)(<\/body[^>]*>.*)/si) {
		print "$1$2\n";
	} else {
		print "$foot\n";
		print "</body></html>\n";
	}
	exit;
}

#-----------------------------------------------------------
#  back属性チェック
#-----------------------------------------------------------
sub chk_back {
	my $back = shift;

	if ($back !~ /^https?:\/\/[\w-.!~*'();\/?:\@&=+\$,%#]+$/i) {
		error("BACK属性が不正です");
	}
}

#-----------------------------------------------------------
#  商品データ認識
#-----------------------------------------------------------
sub get_data {
	my %cart;
	open(IN,"$cf{datfile}") or error("open err: $cf{datfile}");
	while (<IN>) {
		chomp;
		my ($code) = (split(/<>/))[0];

		$cart{$code} = $_;
	}
	close(IN);

	return %cart;
}

#-----------------------------------------------------------
#  コンマ区切
#-----------------------------------------------------------
sub comma {
	local($_) = @_;

	1 while s/(.*\d)(\d\d\d)/$1,$2/;
	$_;
}

#-----------------------------------------------------------
#  消費税
#-----------------------------------------------------------
sub tax_per {
	my $all = shift;
	
	my $kei = $all;
	my $tax;
	if ($cf{tax_per} != 0) {
		$tax = int($all * $cf{tax_per} / 100);
		$all += $tax;
	}
	return ($kei,$tax,$all);
}



1;

