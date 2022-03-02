import deepl
translator = deepl.Translator("4e634b6f-090a-5e11-8acb-19dc8b5b1d4b:fx")
result = translator.translate_text("Casse noix", target_lang="EN-US")
translated_text = result.text
print(translated_text)
