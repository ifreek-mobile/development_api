# 1P男性文章：コーク登場
TEXT_1P_MAN = """こどもディスコへようこそ
{name}くん、きょうはダンスやDJたいけんがたのしめるよ
さぁ、まずはダンスしてみよう！
"""

# 1P女性文章：コーク登場
TEXT_1P_WOMAN = """こどもディスコへようこそ
{name}ちゃん、きょうはダンスやDJたいけんがたのしめるよ
さぁ、まずはダンスしてみよう！
"""

# 2P男性文章：お子さんがダンスを楽しむ
TEXT_2P_MAN = """そうそう、そのちょうし！{name}くん、すごくじょうずだよ！リズムにのって、もっとダンスをたのしんじゃお！
"""

# 2P女性文章：お子さんがダンスを楽しむ
TEXT_2P_WOMAN = """そうそう、そのちょうし！{name}ちゃん、すごくじょうずだよ！リズムにのって、もっとダンスをたのしんじゃお！
"""

# 3P男性文章：コークがお子さんをDJ体験へ案内
TEXT_3P_MAN = """つぎはDJたいけんだよ
{name}くんならきっとじょうずにできるよ！
"""

# 3P女性文章：コークがお子さんをDJ体験へ案内
TEXT_3P_WOMAN = """つぎはDJたいけんだよ
{name}ちゃんならきっとじょうずにできるよ！
"""

# 4P男性文章：お子さんが大人になった姿でDJに！
TEXT_4P_MAN = """{name}くんのおんがくにあわせて、みんながおどってる！おとなになったら、すてきなDJになれるかも
きょうはきてくれてありがとう！またね！
"""

# 4P女性文章：お子さんが大人になった姿でDJに！
TEXT_4P_WOMAN = """{name}ちゃんのおんがくにあわせて、みんながおどってる！おとなになったら、すてきなDJになれるかも
きょうはきてくれてありがとう！またね！
"""

# 2P用の顔の特徴判定プロンプト 子供のダンス姿に使用する
FACE_FEATURE_PROMPT = """
#前提条件
アップされた画像を元に、{gender}の子供の顔の特徴を説明する画像生成プロンプトを生成することが求められます。

ASSISTANT（あなた）は画像生成の専門家です。

#ステップ
[1]画像を元に以下の項目にフォーカスをして子供の顔の特徴をプロンプト形式で出力して、
特に髪色髪型髪の長さについては具体的に記述してください。アクセサリーなどの装飾品がある場合はそれについても記述してください。
・髪色髪型髪の長さ
・目
・口
・輪郭
例)
髪色髪型髪の長さ: 黒髪で、やや長めのショートヘア。自然なストレートで、前髪が額にかかり、サイドは耳を覆わない程度。
目: 大きくて丸い目。黒目がちで瞳がキラキラと輝き、優しい印象を与える。
口: 小さめで、自然な形の唇。ほのかに微笑んでいる表情。
輪郭: やや丸みを帯びた輪郭で、子供らしい柔らかいラインが特徴的。

[2]ステップ1で抽出した特徴を画像生成用のプロンプトに英語でまとめる。

#最終的な出力形式
英語で生成されたプロンプト

#出力例
A young child with black hair in a slightly long, natural straight style. The hair is cut in a short length, with bangs slightly covering the forehead, and the sides do not cover the ears. The child has large, round eyes with dark irises that sparkle, giving a gentle and kind expression. The lips are small and naturally shaped, with a slight smile. The face has a rounded contour, featuring soft lines characteristic of a young child

#注意事項
ステップ[1]の内容は出力しないようにしてください。
ステップ[2]の内容のみを出力してください。
"""

# 2P用のダンスページの画像生成プロンプト
DANCE_IMAGE_PROMPT = """dancing energetically on a vibrant neon-lit dance floor, colorful spotlights creating dynamic patterns across the room, surrounded by arcade machines with glowing buttons and screens, a retro-futuristic club atmosphere, in a cartoonish anime style, vibrant and saturated colors, dynamic poses and expressive movement, A manga style illustration aimed at elementary school children
"""

# 4P用の顔の特徴判定プロンプトから大人への変換プロンプト
# FACE_TO_ADULT_PROMPT = """
# #前提条件
# アップされた子供の顔写真をもとに、大人の顔の特徴を生成する{gender}の画像プロンプトを作成してください。
# ASSISTANT（あなた）は画像生成の専門家です。

# #ステップ

# [1]
# 画像を元に以下の項目にフォーカスして「子供の顔の特徴」を抽出し、
# それをもとに「大人の顔」に変換した特徴を考慮してください。
# - 髪色・髪型・髪の長さ（具体的に）
# - 目
# - 口
# - 輪郭
# - アクセサリー等（もしあれば）
# ※ 子供特有の要素を自然に大人へ成長させたイメージを意識し、髪のスタイルや輪郭などは大人らしくアップデートしてください。

# 例)
# 髪色・髪型・髪の長さ:元の子供が黒髪ショートで前髪あり → 大人の髪型では黒髪ショートで前髪ありなど同じスタイルを維持
# 目:元の子供が丸く大きな目 → 大人の目もやや大きめだが落ち着きのある印象
# 口:元の子供が小さめで自然な形 → 大人でも大きく崩さず、ややふっくら感のある自然な形
# 輪郭:元の子供が丸みを帯びた輪郭 → 大人はややシャープさを足しつつも、面影を残すように

# [2]
# ステップ[1]で抽出・変換した「大人の顔の特徴」を英語でまとめ、画像生成に用いるプロンプトを作成してください。

# #最終的な出力形式
# 英語で生成されたプロンプト

# #出力例
# An adult woman with medium-length black hair, styled in a natural, slightly flowing manner, with a slight side-swept bang. She has large, somewhat rounded eyes that convey a calm yet warm impression, and a naturally shaped mouth with a subtle fullness. Her facial contour is softly defined, retaining a hint of youthful roundness but with a more mature structure.

# #注意事項
# - ステップ[1]の内容は出力しないでください。
# - ステップ[2]の内容のみ出力してください。
# """

FACE_TO_ADULT_PROMPT = """
#前提条件
子供の顔の特徴のプロンプト：[{child_face_prompt}]を元に子供の顔のプロンプトのワードを大人の顔の特徴に変換する画像生成プロンプトを生成してください。

# 入力例
A young child with black hair styled in two braids that fall on either side of her face. The hair is shiny and silky, with soft bangs grazing her forehead. She has large, expressive dark eyes that sparkle, exuding innocence and curiosity. Her lips are small and softly rounded, displaying a gentle smile. The face features a slightly rounded contour, embodying the soft and sweet characteristics typical of a young child

# 出力例
An adult woman with black hair styled in two elegant braids that fall gracefully over her shoulders. The hair is glossy and smooth, with soft bangs framing her face. She has large, expressive dark eyes that shimmer with intelligence and confidence. Her lips are naturally full and gently curved, displaying a warm, welcoming smile. The face features a well-defined contour, embodying sophistication and maturity, while retaining a gentle and approachable demeanor

# 注意事項
髪型などの特徴の変更は加えないように。
"""

# 4P用の大人のダンス姿の画像生成プロンプト
# ADULT_DJ_IMAGE_PROMPT = """
# performing on a futuristic neon-lit DJ booth, colorful spotlights shining from above, vinyl turntables and glowing speakers pulsing to the beat, the crowd's silhouettes in the background, retro-futuristic club atmosphere, in a cartoonish anime style, vibrant and saturated colors, dynamic lighting effects, Anime Style
# """

# 4P用の大人のダンス姿の画像生成プロンプト2
ADULT_DJ_IMAGE_PROMPT = """performing energetically on a futuristic neon-lit DJ booth, colorful spotlights shining from above, vinyl turntables and glowing speakers pulsing to the beat, the crowd's silhouettes dancing in the background, retro-futuristic club atmosphere, in a cartoonish anime style, vibrant and saturated colors, dynamic lighting effects, A manga style illustration aimed at elementary school children, wearing an oversized T-shirt
"""
