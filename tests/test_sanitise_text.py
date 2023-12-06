import pytest

from notifications_utils.sanitise_text import (
    SanitiseASCII,
    SanitiseSMS,
    SanitiseText,
)

params, ids = zip(
    (("a", "a"), "ascii char (a)"),
    # ascii control char (not in GSM)
    (("\t", " "), "ascii control char not in gsm (tab)"),
    # TODO we support lots of languages now not in the GSM charset so maybe make this 'downgrading' go away
    # TODO for now comment out this line because it directly conflicts with support for Turkish
    # these are not in GSM charset so are downgraded
    # (("ç", "c"), "decomposed unicode char (C with cedilla)"),
    # these unicode chars should change to something completely different for compatibility
    (("–", "-"), "compatibility transform unicode char (EN DASH (U+2013)"),
    (("—", "-"), "compatibility transform unicode char (EM DASH (U+2014)"),
    (
        ("…", "..."),
        "compatibility transform unicode char (HORIZONTAL ELLIPSIS (U+2026)",
    ),
    (("\u200B", ""), "compatibility transform unicode char (ZERO WIDTH SPACE (U+200B)"),
    (
        ("‘", "'"),
        "compatibility transform unicode char (LEFT SINGLE QUOTATION MARK (U+2018)",
    ),
    (
        ("’", "'"),
        "compatibility transform unicode char (RIGHT SINGLE QUOTATION MARK (U+2019)",
    ),
    (
        ("“", '"'),
        "compatibility transform unicode char (LEFT DOUBLE QUOTATION MARK (U+201C)	",
    ),
    (
        ("”", '"'),
        "compatibility transform unicode char (RIGHT DOUBLE QUOTATION MARK (U+201D)",
    ),
    (("\xa0", " "), "nobreak transform unicode char (NO-BREAK SPACE (U+00A0))"),
    # this unicode char is not decomposable
    (("😬", "?"), "undecomposable unicode char (grimace emoji)"),
    (("↉", "?"), "vulgar fraction (↉) that we do not try decomposing"),
)


@pytest.mark.parametrize("char, expected", params, ids=ids)
@pytest.mark.parametrize("cls", [SanitiseSMS, SanitiseASCII])
def test_encode_chars_the_same_for_ascii_and_sms(char, expected, cls):
    assert cls.encode_char(char) == expected


params, ids = zip(
    # ascii control chars are allowed in GSM but not in ASCII
    (("\n", "\n", "?"), "ascii control char in gsm (newline)"),
    (("\r", "\r", "?"), "ascii control char in gsm (return)"),
    # These characters are present in GSM but not in ascii
    (("à", "à", "a"), "non-ascii gsm char (a with accent)"),
    (("€", "€", "?"), "non-ascii gsm char (euro)"),
    # These characters are Welsh characters that are not present in GSM
    (("â", "â", "a"), "non-gsm Welsh char (a with hat)"),
    (("Ŷ", "Ŷ", "Y"), "non-gsm Welsh char (capital y with hat)"),
    (("ë", "ë", "e"), "non-gsm Welsh char (e with dots)"),
    # (("Ò", "Ò", "O"), "non-gsm Welsh char (capital O with grave accent)"),  # conflicts with Vietnamese
    (("í", "í", "i"), "non-gsm Welsh char (i with accent)"),
)


@pytest.mark.parametrize("char, expected_sms, expected_ascii", params, ids=ids)
def test_encode_chars_different_between_ascii_and_sms(
    char, expected_sms, expected_ascii
):
    assert SanitiseSMS.encode_char(char) == expected_sms
    assert SanitiseASCII.encode_char(char) == expected_ascii


@pytest.mark.parametrize(
    "codepoint, char",
    [
        ("0041", "A"),
        ("0061", "a"),
    ],
)
def test_get_unicode_char_from_codepoint(codepoint, char):
    assert SanitiseText.get_unicode_char_from_codepoint(codepoint) == char


@pytest.mark.parametrize(
    "bad_input", ["", "GJ", "00001", '0001";import sys;sys.exit(0)"']
)
def test_get_unicode_char_from_codepoint_rejects_bad_input(bad_input):
    with pytest.raises(ValueError):
        SanitiseText.get_unicode_char_from_codepoint(bad_input)


@pytest.mark.parametrize(
    "content, expected",
    [
        ("Łōdź", "?odz"),
        (
            "The quick brown fox jumps over the lazy dog",
            "The quick brown fox jumps over the lazy dog",
        ),
    ],
)
def test_encode_string(content, expected):
    assert SanitiseSMS.encode(content) == expected
    assert SanitiseASCII.encode(content) == expected


@pytest.mark.parametrize(
    "content, cls, expected",
    [
        ("The quick brown fox jumps over the lazy dog", SanitiseSMS, set()),
        (
            "The “quick” brown fox has some downgradable characters\xa0",
            SanitiseSMS,
            set(),
        ),
        ("Need more 🐮🔔", SanitiseSMS, {"🐮", "🔔"}),
        ("Ŵêlsh chârâctêrs ârê cômpâtîblê wîth SanitiseSMS", SanitiseSMS, set()),
        ("Lots of GSM chars that arent ascii compatible:\n\r€", SanitiseSMS, set()),
        (
            "Lots of GSM chars that arent ascii compatible:\n\r€",
            SanitiseASCII,
            {"\n", "\r", "€"},
        ),
        ("Αυτό είναι ένα τεστ", SanitiseSMS, set()),
    ],
)
def test_sms_encoding_get_non_compatible_characters(content, cls, expected):
    assert cls.get_non_compatible_characters(content) == expected


@pytest.mark.parametrize(
    "content, expected",
    [
        ("이것은 테스트입니다", True),  # Korean
        ("Αυτό είναι ένα τεστ", True),  # Greek
        ("Это проверка", True),  # Russian
        ("นี่คือการทดสอบ", True),  # Thai
        ("இது ஒரு சோதனை", True),  # Tamil
        ("これはテストです", True),  # Japanese
        ("Đây là một bài kiểm tra", True),  # Vietnamese
        ("𐤓𐤓𐤓𐤈𐤆", False),  # Phoenician
        ("这是一次测试", True),  # Mandarin (Simplified)
        ("Bunda Türkçe karakterler var", True),  # Turkish
        (
            "盾牌镍币是第一种采用白铜制作的5美分硬币，由詹姆斯·B·朗埃克设计，从1866年发行到1883年再由自由女神头像镍币取代。",
            True,
        ),  # Chinese from wikipedia 1
        (
            "国际志愿者日為每年的12月5日，它是由联合国大会在1985年12月17日通过的A/RES/40/212决议[1]上确定的[2]。",
            True,
        ),  # Chinese from wikipedia 2
        ("哪一種多邊形內部至少存在一個可以看見多邊形所有邊界和所有內部區域的點？", True),  # Chinese from wikipedia 3
        (
            "都柏林在官方城市邊界內的人口是大約495,000人（愛爾蘭中央統計處2002年人口調查），然而這種統計已經沒有什麼太大的意義，因為都柏林的市郊地區和衛星城鎮已經大幅地發展與擴張。",
            True,
        ),  # noqa too long # Chinese from wikipedia 4
        (
            "一名是Dubh Linn（愛爾蘭語，意為「黑色的水池」）的英國習語。當然也有人質疑這語源。",
            True,
        ),  # Chinese from wikipedia 5
        (
            "都柏林拥有世界闻名的文学历史，曾经产生过许多杰出的文学家，例如诺贝尔文学奖得主威廉·巴特勒·叶芝、蕭伯納和塞繆爾·貝克特。",
            True,
        ),  # Chinese from wikipedia 6
        (
            "愛爾蘭國家博物館的四个分馆中有三個分館都位於都柏林：考古学分馆在基尔代尔街，装饰艺术和历史分馆在柯林斯军营，而自然史分馆在梅林街[12]。",
            True,
        ),  # Chinese from wikipedia 7
        (
            "從17世紀開始，城市在寬闊街道事務委員會的幫助下開始迅速擴張。乔治亚都柏林曾一度是大英帝國僅次於倫敦的第二大城市。",
            True,
        ),  # Chinese from wikipedia 8
        ("一些著名的都柏林街道建築仍以倒閉前在此經營的酒吧和商業公司命名。", True),  # Chinese from wikipedia 9
        (
            "1922年，隨著愛爾蘭的分裂，都柏林成為愛爾蘭自由邦（1922年–1937年）的首都。現在則為愛爾蘭共和國的首都。",
            True,
        ),  # Chinese from wikipedia 10
        (
            "Dưới đây là danh sách tất cả các tên người dùng hiện đang có tại Wikipedia, hoặc những tên người dùng trong một nhóm chỉ định. ",  # noqa too long
            True,
        ),  # Vietnamese from wikipedia 1
        (
            "Các bảo quản viên đảm nhận những trách nhiệm này với tư cách là tình nguyện viên sau khi trải qua quá trình xem xét của cộng đồng. ",  # noqa too long
            True,
        ),  # Vietnamese from wikipedia 2
        (
            'Họ không bao giờ được yêu cầu sử dụng các công cụ của mình và không bao giờ được sử dụng chúng để giành lợi thế trong một cuộc tranh chấp mà họ có tham gia. Không nên nhầm lẫn bảo quản viên với quản trị viên hệ thống của Wikimedia ("sysadmins").',  # noqa too long
            True,
        ),  # Vietnamese from wikipedia 3
        (
            "Để đạt được mục tiêu chung đó, Wikipedia đề ra một số quy định và hướng dẫn. ",
            True,
        ),  # Vietnamese from wikipedia 4
        ("Wikipedia là một bách khoa toàn thư. ", True),  # Vietnamese from wikipedia 5
        (
            "Phải đảm bảo bài viết mang lại ích lợi cho độc giả (coi độc giả là yếu tố quan trọng khi viết bài)",
            True,
        ),  # Vietnamese from wikipedia 6
        (
            "Bài viết ở Wikipedia có thể chứa đựng từ ngữ và hình ảnh gây khó chịu nhưng chỉ vì mục đích tốt đẹp. Không cần thêm vào phủ định trách nhiệm.",  # noqa too long
            True,
        ),  # Vietnamese from wikipedia 7
        (
            "Đừng sử dụng hình ảnh mà chỉ có thể xem được chính xác với công cụ 3D.",
            True,
        ),  # Vietnamese from wikipedia 8
        (
            "Trích dẫn bất cứ nôi dung tranh luận gốc nào cũng nên có liên quan đến tranh luận đó (hoặc minh họa cho phong cách) và chỉ nên dài vừa đủ.",  # noqa too long
            True,
        ),  # Vietnamese from wikipedia 9
        (
            "Không tung tin vịt, thông tin sai lệch hoặc nội dung không kiểm chứng được vào bài viết. Tuy nhiên, những bài viết về những tin vịt nổi bật được chấp nhận.",  # noqa too long
            True,
        ),  # Vietnamese from wikipedia 10
        (
            "수록되어 있으며, 넘겨주기를 포함한 일반 문서 수는 1,434,776개。",
            True,
        ),  # Korean from wikipedia includes circle-period
        (
            "日本語表記にも対応するようになり[1]、徐々に日本人のユーザーも増大していった、と述べられている。",
            True,
        ),  # Japanese from wikipedia includes circle-period
    ],
)
def test_sms_supporting_additional_languages(content, expected):
    assert SanitiseSMS.is_extended_language(content) is expected


@pytest.mark.parametrize(
    "content, expected",
    [
        ("이것은 테스트입니다", set()),  # Korean
        ("Αυτό είναι ένα τεστ", set()),  # Greek
        ("Это проверка", set()),  # Russian
        ("นี่คือการทดสอบ", set()),  # Thai
        ("இது ஒரு சோதனை", set()),  # Tamil
        ("これはテストです", set()),  # Japanese
        ("Đây là một bài kiểm tra", set()),  # Vietnamese
        ("𐤓𐤓𐤓𐤈𐤆", {"𐤆", "𐤈", "𐤓"}),  # Phoenician
        ("这是一次测试", set()),  # Mandarin (Simplified)
        ("Bunda Türkçe karakterler var", set()),  # Turkish
    ],
)
def test_get_non_compatible_characters(content, expected):
    assert SanitiseSMS.get_non_compatible_characters(content) == expected
