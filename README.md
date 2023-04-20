# TransLaTeX

TransLaTeX is a lightweighted command line tool for translating LaTeX projects. By parsing and splitting the LaTeX content and leveraging GPT's capabilities, TransLaTeX can automatically translate content from any language to any other language.

## How does it work?

1. Parse the main document source file and recursively find all referenced .tex source files.
2. Automatically divide the LaTeX texts into smaller pieces with a proper size (smaller than a given chunk size).
3. Use ChatGPT to translate all of the LaTeX texts.
4. Create a new project with the translated files, keeping the project structure unchanged.
5. Compile the source and obtain the translated paper! (by yourself)

## Quick Start

Create a Python environment and install the required dependencies.

```bash
conda create -n translatex python==3.9
pip install -r requirements.txt
```

Download the LaTeX source of the paper to be translated. E.g. go to an arXiv abs page -> "Other Formats" -> "Download Source" -> extract the .tar.gz file.

Prepare your OpenAI API key. You can provide the key as a command-line argument `--api_key`, or save the key in the file `./openai-api-key`.

Run the `main.py` script in the root directory.

```bash
conda activate translatex
python ./main.py /path/to/latex/project
```
