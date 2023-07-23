from langchain import LangChain
latex_translation_prompt = f"""Translate LaTeX text from {{src_lang}} into {{tgt_lang}}. 
These texts are from a academic research paper so your translation should follow guidelines of academic writing.
You should only translate the plain text and your outputs are in LaTeX format.
You are allowed to keep some special terms in English if they can not be translated into {{tgt_lang}} precisely.
You should not change any LaTeX macros, neither the command names nor the arguments.
You should not translate the words in math expressions.
Both the texts to be translated and your translations are enclosed in triple quotes. 
Ensure your output can be parsed successfully by LaTeX compilers.
\"\"\"{{latex_text}}\"\"\"
"""

latex_translation_prompt = f"""Translate academic research paper text in LaTeX format from {{src_lang}} to {{tgt_lang}}. 
Only translate plain text and keep the special {{src_lang}} terms that cannot be translated precisely. 
Your translations should follow academic writing guidelines. 
Do not change any LaTeX macros or math expressions. 
Both the texts to be translated and your translations are enclosed in triple quotes.
Ensure your output can be parsed successfully by LaTeX compilers.
\"\"\"{{latex_text}}\"\"\""""


default_system = 'You are a helpful assistant.'
def get_prompt(text, src_lang='English', tgt_lang='Chinese'):
    lang_chain = LangChain()
    translated_text = lang_chain.translate(text, src_lang, tgt_lang)
    return translated_text
