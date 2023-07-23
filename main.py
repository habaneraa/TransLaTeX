import shutil
import os
import argparse
import openai

from latextranslator import LatexTranslator


def main():
    argparser = argparse.ArgumentParser('latextranslator')
    argparser.add_argument('dir', type=str, help='root directory of the LaTeX project to be translated (should contain a main document source file).')
    argparser.add_argument('-o', '--output', type=str, default=None, help='output directory for translated files')
    argparser.add_argument('--main', type=str, default=None, help='name of the main document file')
    argparser.add_argument('--source_language', type=str, default='English', help='source language of the LaTeX files. e.g., \"English\"')
    argparser.add_argument('--target_language', type=str, default='Chinese', help='target language for translation. e.g., \"Chinese\"')
    argparser.add_argument('--api_key', type=str, default=None, help='API key of OpenAI')
    argparser.add_argument('--api_key_path', type=str, default='./openai-api-key', help='path to file containing API key')

    args = argparser.parse_args()

    # get api key
    openai.api_key = os.environ.get('OPENAI_API_KEY')
    if args.api_key is not None:
        openai.api_key = args.api_key
    else:
        if not openai.api_key:
            with open(args.api_key_path, 'r') as f:
                api_key = f.read().strip()
            openai.api_key = api_key

    # prepare output directory
    if args.output is None:
        args.dir = os.path.normpath(args.dir)
        args.output = os.path.join(os.path.join(args.dir, os.path.pardir), os.path.basename(args.dir) + '_' + args.target_language)
    args.output = os.path.realpath(args.output)
    if os.path.exists(args.output) and len(os.listdir(args.output)) > 0:
        print('Warning: path already exists:', args.output)
    os.makedirs(args.output, exist_ok=True)

    # copy non-tex file to the output directory
    print('Copying all sources to output directory:', args.output)
    for root, dirs, files in os.walk(args.dir):
        for file_name in files:
            src_file_path = os.path.join(root, file_name)
            dst_file_path = os.path.join(args.output, os.path.relpath(src_file_path, args.dir))
            os.makedirs(os.path.dirname(dst_file_path), exist_ok=True)
            shutil.copy(src_file_path, dst_file_path)

    # run translator
    translator = LatexTranslator(args.source_language, args.target_language, chunk_size=1000)
    translator.estimate_work(args.dir, args.output, args.main)
    translator.translate_project(args.dir, args.output, args.main)
    translator.show_cost()


if __name__ == '__main__':
    main()
