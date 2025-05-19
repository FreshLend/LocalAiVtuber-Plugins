from pluginInterface import TranslationPluginInterface
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import gradio as gr
from langdetect import detect

class NLLBTranslator(TranslationPluginInterface):
    def init(self):
        model_name = "facebook/nllb-200-distilled-600M"
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        
        self.input_lang = 'auto'  # auto detect
        self.output_lang = 'eng_Latn'  # lang default (english)
        
        self.language_mapping = {
            'en': 'eng_Latn',  # English
            'ru': 'rus_Cyrl',  # Russian
            'es': 'spa_Latn',  # Spanish
            'fr': 'fra_Latn',  # French
            'de': 'deu_Latn',  # German
            'zh': 'zho_Hans',  # Chinese (Simplified)
            'ja': 'jpn_Jpan',  # Japanese
            'ar': 'arb_Arab',  # Arabic
            'pt': 'por_Latn',  # Portuguese
            'it': 'ita_Latn',  # Italian
            'nl': 'nld_Latn',  # Dutch
            'hi': 'hin_Deva',  # Hindi
            'ko': 'kor_Hang',  # Korean
            'tr': 'tur_Latn',  # Turkish
            'pl': 'pol_Latn',  # Polish
            'th': 'tha_Thai',  # Thai
            'vi': 'vie_Latn',  # Vietnamese
            'id': 'ind_Latn',  # Indonesian
            'uk': 'ukr_Cyrl',  # Ukrainian
            'fa': 'pes_Arab',  # Persian
            'sv': 'swe_Latn',  # Swedish
            'fi': 'fin_Latn',  # Finnish
            'da': 'dan_Latn',  # Danish
            'no': 'nor_Latn',  # Norwegian
            'he': 'heb_Hebr',  # Hebrew
            'el': 'ell_Grek',  # Greek
            'ro': 'ron_Latn',  # Romanian
            'hu': 'hun_Latn',  # Hungarian
            'cs': 'ces_Latn',  # Czech
            'sk': 'slk_Latn',  # Slovak
            'bg': 'bul_Cyrl',  # Bulgarian
            'sr': 'srp_Cyrl',  # Serbian
            'hr': 'hrv_Latn',  # Croatian
            'bn': 'ben_Beng',  # Bengali
            'ta': 'tam_Taml',  # Tamil
            'te': 'tel_Telu',  # Telugu
            'mr': 'mar_Deva',  # Marathi
            'ur': 'urd_Arab',  # Urdu
            'ms': 'zsm_Latn',  # Malay
            'tl': 'tgl_Latn',  # Tagalog
        }
        
        self.reverse_language_mapping = {v: k for k, v in self.language_mapping.items()}

    def translate(self, text):
        if not text.strip():
            return ""
            
        if self.input_lang == 'auto':
            try:
                detected_lang = detect(text)
                src_lang = self.language_mapping.get(detected_lang, 'eng_Latn')
            except:
                src_lang = 'eng_Latn'  # fallback
        else:
            src_lang = self.language_mapping.get(self.input_lang, 'eng_Latn')
        
        tgt_lang = self.output_lang
        
        self.tokenizer.src_lang = src_lang
        
        inputs = self.tokenizer(text, return_tensors="pt")
        
        forced_bos_token_id = self.tokenizer.convert_tokens_to_ids(tgt_lang)
        
        translated_tokens = self.model.generate(
            **inputs,
            forced_bos_token_id=forced_bos_token_id,
            max_new_tokens=1000
        )
        
        return self.tokenizer.decode(translated_tokens[0], skip_special_tokens=True)

    def get_input_language_code(self):
        return self.input_lang

    def get_output_language_code(self):
        return self.output_lang.split('_')[0]

    def create_ui(self):
        language_choices = [
            ("English", "eng_Latn"),
            ("Русский", "rus_Cyrl"),
            ("Español", "spa_Latn"),
            ("Français", "fra_Latn"),
            ("Deutsch", "deu_Latn"),
            ("中文", "zho_Hans"),
            ("日本語", "jpn_Jpan"),
            ("العربية", "arb_Arab"),
            ("Português", "por_Latn"),
            ("Italiano", "ita_Latn"),
            ("Nederlands", "nld_Latn"),
            ("हिन्दी", "hin_Deva"),
            ("한국어", "kor_Hang"),
            ("Türkçe", "tur_Latn"),
            ("Polski", "pol_Latn"),
            ("ไทย", "tha_Thai"),
            ("Tiếng Việt", "vie_Latn"),
            ("Bahasa Indonesia", "ind_Latn"),
            ("Українська", "ukr_Cyrl"),
            ("فارسی", "pes_Arab"),
            ("Svenska", "swe_Latn"),
            ("Suomi", "fin_Latn"),
            ("Dansk", "dan_Latn"),
            ("Norsk", "nor_Latn"),
            ("עברית", "heb_Hebr"),
            ("Ελληνικά", "ell_Grek"),
            ("Română", "ron_Latn"),
            ("Magyar", "hun_Latn"),
            ("Čeština", "ces_Latn"),
            ("Slovenčina", "slk_Latn"),
            ("Български", "bul_Cyrl"),
            ("Српски", "srp_Cyrl"),
            ("Hrvatski", "hrv_Latn"),
            ("বাংলা", "ben_Beng"),
            ("தமிழ்", "tam_Taml"),
            ("తెలుగు", "tel_Telu"),
            ("मराठी", "mar_Deva"),
            ("اردو", "urd_Arab"),
            ("Bahasa Melayu", "zsm_Latn"),
            ("Filipino", "tgl_Latn"),
        ]
        
        with gr.Accordion(label="Translation Settings", open=False):
            with gr.Row():
                self.input_lang_dropdown = gr.Dropdown(
                    choices=[("Auto detect", "auto")] + [(lang[0], self.language_mapping[lang[1]]) 
                        for lang in [
                            ("English", "en"),
                            ("Русский", "ru"),
                            ("Español", "es"),
                            ("Français", "fr"),
                            ("Deutsch", "de"),
                            ("中文", "zh"),
                            ("日本語", "ja"),
                            ("العربية", "ar"),
                            ("Português", "pt"),
                            ("Italiano", "it"),
                            ("Nederlands", "nl"),
                            ("हिन्दी", "hi"),
                            ("한국어", "ko"),
                            ("Türkçe", "tr"),
                            ("Polski", "pl"),
                            ("ไทย", "th"),
                            ("Tiếng Việt", "vi"),
                            ("Bahasa Indonesia", "id"),
                            ("Українська", "uk"),
                            ("فارسی", "fa"),
                            ("Svenska", "sv"),
                            ("Suomi", "fi"),
                            ("Dansk", "da"),
                            ("Norsk", "no"),
                            ("עברית", "he"),
                            ("Ελληνικά", "el"),
                            ("Română", "ro"),
                            ("Magyar", "hu"),
                            ("Čeština", "cs"),
                            ("Slovenčina", "sk"),
                            ("Български", "bg"),
                            ("Српски", "sr"),
                            ("Hrvatski", "hr"),
                            ("বাংলা", "bn"),
                            ("தமிழ்", "ta"),
                            ("తెలుగు", "te"),
                            ("मराठी", "mr"),
                            ("اردو", "ur"),
                            ("Bahasa Melayu", "ms"),
                            ("Filipino", "tl")
                        ]],
                    value=self.input_lang,
                    label="Source Language"
                )
                self.output_lang_dropdown = gr.Dropdown(
                    choices=language_choices,
                    value=self.output_lang,
                    label="Target Language"
                )

            self.input_lang_dropdown.change(
                lambda x: setattr(self, 'input_lang', x),
                inputs=self.input_lang_dropdown,
                outputs=None
            )
            self.output_lang_dropdown.change(
                lambda x: setattr(self, 'output_lang', x),
                inputs=self.output_lang_dropdown,
                outputs=None
            )