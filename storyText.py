with open("assets/storyErdrutsch.md", "r", encoding="utf-8") as f:
    text = f.readlines()
    text = [ln for ln in text if ln != "\n"]
    (
        title,
        desc,
        author,
        subtitle1,
        text1,
        text2,
        pic1,  # Bild
        text3,
        text4,
        text5,
        pic2,  # Bild
        text6,
        text7,
        text8,
        subtitle2,
        text9,
        text10,
        pic3,  # Plot Temp
        text11,
        text12,
        text13,
        text14,
        pic4,  # Plot Snow
        text15,
        pic5,  # Plot Rain
        text16,
        text17,
        pic6,  # Plot Rain Extreme
        text18,
        subtitle3,
        text19,
        text20,
        text21,
        # Sep
        sep,
        subtitle4,
        text22,
        text23,
        text24
    ) = text
