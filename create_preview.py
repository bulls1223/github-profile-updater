import markdown
import os

INPUT_FILE = "GENERATED_PROFILE.md"
OUTPUT_FILE = "GENERATED_PROFILE.html"

def convert_to_html():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found.")
        return

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        text = f.read()

    # Convert Markdown to HTML
    html_content = markdown.markdown(text)

    # Basic GitHub-like CSS
    styled_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Profile Preview</title>
        <style>
            body {{
                font-family: -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif,"Apple Color Emoji","Segoe UI Emoji";
                line-height: 1.6;
                color: #24292e;
                max-width: 800px;
                margin: 0 auto;
                padding: 40px 20px;
            }}
            h1, h2, h3 {{ border-bottom: 1px solid #eaecef; padding-bottom: 0.3em; }}
            h1 {{ font-size: 2em; }}
            h2 {{ font-size: 1.5em; margin-top: 24px; }}
            a {{ color: #0366d6; text-decoration: none; }}
            a:hover {{ text-decoration: underline; }}
            blockquote {{ color: #6a737d; border-left: 0.25em solid #dfe2e5; padding: 0 1em; margin: 0; }}
            code {{ background-color: rgba(27,31,35,.05); border-radius: 3px; font-size: 85%; margin: 0; padding: .2em .4em; }}
        </style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(styled_html)
    
    print(f"Successfully created HTML preview: {OUTPUT_FILE}")

if __name__ == "__main__":
    convert_to_html()
