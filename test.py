from pprint import pprint
import pymupdf

doc = pymupdf.open(
    "./data/samples/Chapter 2 University Procurement Services Procedures Manual_0.pdf")



for page in doc:
    title: str  = ""
    heading: str = ""
    section: str = ""
    copyright: str = ""
    blocks = page.get_text("blocks",sort=True)
    for block in blocks:
        print("=" * 80)
        x0,y0,x1,y1,text,block_no,block_type = block[:7]
        if text.strip():
            # print(f"position: ({x0:.1f}, {y0:.1f}) -> ({x1:.1f}, {y1:.1f})")
            # print(f"block_no: {block_no}, type: {block_type}")
            # print(repr(text))
            # print(text.rstrip()[-1])
            if text.rstrip()[-1] == ":":
                title = text.rstrip()
                print(f"Title -- {title}")
            elif text.strip().startswith("©"):
                copyright = text.strip()
                print(f"Copyright -- {copyright}")
            break






for page_no, page in enumerate(doc):

    print(f"\n{'#' * 20} PAGE {page_no + 1} {'#' * 20}")

    data = page.get_text("dict", sort=True)

    for block in data["blocks"]:

        if block["type"] != 0:
            continue

        for line in block["lines"]:

            text = "".join(
                span["text"]
                for span in line["spans"]
            ).strip()

            if not text:
                continue

            print(repr(text))

