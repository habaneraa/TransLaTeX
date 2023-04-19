# TransLaTeX

TransLaTeX is a lightweighted command line tool for translating LaTeX projects. By parsing and splitting the LaTeX content and leveraging GPT's capabilities, TransLaTeX can automatically translate content from any language to any other language.

## How does it work?

1. Parse the main document source file and recursively find all referenced .tex source files.
2. Automatically divide the LaTeX texts into smaller pieces with a proper size (smaller than a given chunk size).
3. Use ChatGPT to translate all of the LaTeX texts.
4. Create a new project with the translated files, keeping the project structure unchanged.
5. Compile the source and obtain the translated paper! (by yourself)

## Quick start:

1. Create a Python environment and install the required dependencies.
2. Download the LaTeX source of the paper to be translated.
3. Provide the OpenAI API key as a command-line argument, or save the key in the file `openai-api-key`.
4. Run the `main.py` script in the root directory and pass the path of your LaTeX project to it.

### Example

```shell
# Provide the OpenAI API key as a file `./openai-api-key`
./main.py <latex-src-dir>

# Provide the OpenAI API key as a command-line argument
./main.py <latex-src-dir> --api_key <openai-api-key>
```

## Tips
