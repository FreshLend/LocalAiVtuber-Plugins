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
            'aa': 'gaz_Latn',  # Afar
            'ab': 'abk_Cyrl',  # Abkhazian
            'af': 'afr_Latn',  # Afrikaans
            'am': 'amh_Ethi',  # Amharic
            'ar': 'arb_Arab',  # Arabic (Standard)
            'as': 'asm_Beng',  # Assamese
            'ay': 'aym_Latn',  # Aymara
            'az': 'azj_Latn',  # Azerbaijani
            'ba': 'bak_Cyrl',  # Bashkir
            'be': 'bel_Cyrl',  # Belarusian
            'bg': 'bul_Cyrl',  # Bulgarian
            'bn': 'ben_Beng',  # Bengali
            'bo': 'bod_Tibt',  # Tibetan
            'br': 'bre_Latn',  # Breton
            'bs': 'bos_Latn',  # Bosnian
            'ca': 'cat_Latn',  # Catalan
            'ce': 'che_Cyrl',  # Chechen
            'co': 'cos_Latn',  # Corsican
            'cs': 'ces_Latn',  # Czech
            'cv': 'chv_Cyrl',  # Chuvash
            'cy': 'cym_Latn',  # Welsh
            'da': 'dan_Latn',  # Danish
            'de': 'deu_Latn',  # German
            'el': 'ell_Grek',  # Greek
            'en': 'eng_Latn',  # English
            'eo': 'epo_Latn',  # Esperanto
            'es': 'spa_Latn',  # Spanish
            'et': 'est_Latn',  # Estonian
            'eu': 'eus_Latn',  # Basque
            'fa': 'pes_Arab',  # Persian
            'fi': 'fin_Latn',  # Finnish
            'fj': 'fij_Latn',  # Fijian
            'fo': 'fao_Latn',  # Faroese
            'fr': 'fra_Latn',  # French
            'fy': 'fry_Latn',  # Western Frisian
            'ga': 'gle_Latn',  # Irish
            'gd': 'gla_Latn',  # Scottish Gaelic
            'gl': 'glg_Latn',  # Galician
            'gn': 'grn_Latn',  # Guarani
            'gu': 'guj_Gujr',  # Gujarati
            'ha': 'hau_Latn',  # Hausa
            'he': 'heb_Hebr',  # Hebrew
            'hi': 'hin_Deva',  # Hindi
            'hr': 'hrv_Latn',  # Croatian
            'ht': 'hat_Latn',  # Haitian Creole
            'hu': 'hun_Latn',  # Hungarian
            'hy': 'hye_Armn',  # Armenian
            'id': 'ind_Latn',  # Indonesian
            'ig': 'ibo_Latn',  # Igbo
            'is': 'isl_Latn',  # Icelandic
            'it': 'ita_Latn',  # Italian
            'iu': 'iku_Cans',  # Inuktitut
            'ja': 'jpn_Jpan',  # Japanese
            'jv': 'jav_Latn',  # Javanese
            'ka': 'kat_Geor',  # Georgian
            'kk': 'kaz_Cyrl',  # Kazakh
            'kl': 'kal_Latn',  # Kalaallisut
            'km': 'khm_Khmr',  # Khmer
            'kn': 'kan_Knda',  # Kannada
            'ko': 'kor_Hang',  # Korean
            'ku': 'kmr_Latn',  # Kurdish (Northern)
            'ky': 'kir_Cyrl',  # Kyrgyz
            'la': 'lat_Latn',  # Latin
            'lb': 'ltz_Latn',  # Luxembourgish
            'ln': 'lin_Latn',  # Lingala
            'lo': 'lao_Laoo',  # Lao
            'lt': 'lit_Latn',  # Lithuanian
            'lv': 'lvs_Latn',  # Latvian
            'mg': 'plt_Latn',  # Malagasy
            'mi': 'mri_Latn',  # Maori
            'mk': 'mkd_Cyrl',  # Macedonian
            'ml': 'mal_Mlym',  # Malayalam
            'mn': 'khk_Cyrl',  # Mongolian (Cyrillic)
            'mr': 'mar_Deva',  # Marathi
            'ms': 'zsm_Latn',  # Malay
            'mt': 'mlt_Latn',  # Maltese
            'my': 'mya_Mymr',  # Burmese
            'nb': 'nob_Latn',  # Norwegian Bokmål
            'ne': 'npi_Deva',  # Nepali
            'nl': 'nld_Latn',  # Dutch
            'nn': 'nno_Latn',  # Norwegian Nynorsk
            'no': 'nor_Latn',  # Norwegian
            'oc': 'oci_Latn',  # Occitan
            'om': 'gaz_Latn',  # Oromo
            'or': 'ory_Orya',  # Odia
            'pa': 'pan_Guru',  # Punjabi
            'pl': 'pol_Latn',  # Polish
            'ps': 'pbt_Arab',  # Pashto
            'pt': 'por_Latn',  # Portuguese
            'qu': 'que_Latn',  # Quechua
            'ro': 'ron_Latn',  # Romanian
            'ru': 'rus_Cyrl',  # Russian
            'rw': 'kin_Latn',  # Kinyarwanda
            'sa': 'san_Deva',  # Sanskrit
            'sd': 'snd_Arab',  # Sindhi
            'si': 'sin_Sinh',  # Sinhala
            'sk': 'slk_Latn',  # Slovak
            'sl': 'slv_Latn',  # Slovenian
            'sm': 'smo_Latn',  # Samoan
            'sn': 'sna_Latn',  # Shona
            'so': 'som_Latn',  # Somali
            'sq': 'sqi_Latn',  # Albanian
            'sr': 'srp_Cyrl',  # Serbian
            'ss': 'ssw_Latn',  # Swati
            'st': 'sot_Latn',  # Southern Sotho
            'su': 'sun_Latn',  # Sundanese
            'sv': 'swe_Latn',  # Swedish
            'sw': 'swh_Latn',  # Swahili
            'ta': 'tam_Taml',  # Tamil
            'te': 'tel_Telu',  # Telugu
            'tg': 'tgk_Cyrl',  # Tajik
            'th': 'tha_Thai',  # Thai
            'ti': 'tir_Ethi',  # Tigrinya
            'tk': 'tuk_Latn',  # Turkmen
            'tl': 'tgl_Latn',  # Tagalog
            'tn': 'tsn_Latn',  # Tswana
            'to': 'ton_Latn',  # Tonga
            'tr': 'tur_Latn',  # Turkish
            'ts': 'tso_Latn',  # Tsonga
            'tt': 'tat_Cyrl',  # Tatar
            'ug': 'uig_Arab',  # Uyghur
            'uk': 'ukr_Cyrl',  # Ukrainian
            'ur': 'urd_Arab',  # Urdu
            'uz': 'uzn_Latn',  # Uzbek
            'vi': 'vie_Latn',  # Vietnamese
            'wo': 'wol_Latn',  # Wolof
            'xh': 'xho_Latn',  # Xhosa
            'yi': 'ydd_Hebr',  # Yiddish
            'yo': 'yor_Latn',  # Yoruba
            'zh': 'zho_Hans',  # Chinese (Simplified)
            'zu': 'zul_Latn',  # Zulu
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
            ("Afar", "gaz_Latn"),
            ("Abkhazian", "abk_Cyrl"),
            ("Afrikaans", "afr_Latn"),
            ("Amharic", "amh_Ethi"),
            ("Arabic", "arb_Arab"),
            ("Assamese", "asm_Beng"),
            ("Aymara", "aym_Latn"),
            ("Azerbaijani", "azj_Latn"),
            ("Bashkir", "bak_Cyrl"),
            ("Belarusian", "bel_Cyrl"),
            ("Bulgarian", "bul_Cyrl"),
            ("Bengali", "ben_Beng"),
            ("Tibetan", "bod_Tibt"),
            ("Breton", "bre_Latn"),
            ("Bosnian", "bos_Latn"),
            ("Catalan", "cat_Latn"),
            ("Chechen", "che_Cyrl"),
            ("Corsican", "cos_Latn"),
            ("Czech", "ces_Latn"),
            ("Chuvash", "chv_Cyrl"),
            ("Welsh", "cym_Latn"),
            ("Danish", "dan_Latn"),
            ("German", "deu_Latn"),
            ("Greek", "ell_Grek"),
            ("English", "eng_Latn"),
            ("Esperanto", "epo_Latn"),
            ("Spanish", "spa_Latn"),
            ("Estonian", "est_Latn"),
            ("Basque", "eus_Latn"),
            ("Persian", "pes_Arab"),
            ("Finnish", "fin_Latn"),
            ("Fijian", "fij_Latn"),
            ("Faroese", "fao_Latn"),
            ("French", "fra_Latn"),
            ("Western Frisian", "fry_Latn"),
            ("Irish", "gle_Latn"),
            ("Scottish Gaelic", "gla_Latn"),
            ("Galician", "glg_Latn"),
            ("Guarani", "grn_Latn"),
            ("Gujarati", "guj_Gujr"),
            ("Hausa", "hau_Latn"),
            ("Hebrew", "heb_Hebr"),
            ("Hindi", "hin_Deva"),
            ("Croatian", "hrv_Latn"),
            ("Haitian Creole", "hat_Latn"),
            ("Hungarian", "hun_Latn"),
            ("Armenian", "hye_Armn"),
            ("Indonesian", "ind_Latn"),
            ("Igbo", "ibo_Latn"),
            ("Icelandic", "isl_Latn"),
            ("Italian", "ita_Latn"),
            ("Inuktitut", "iku_Cans"),
            ("Japanese", "jpn_Jpan"),
            ("Javanese", "jav_Latn"),
            ("Georgian", "kat_Geor"),
            ("Kazakh", "kaz_Cyrl"),
            ("Kalaallisut", "kal_Latn"),
            ("Khmer", "khm_Khmr"),
            ("Kannada", "kan_Knda"),
            ("Korean", "kor_Hang"),
            ("Kurdish (Northern)", "kmr_Latn"),
            ("Kyrgyz", "kir_Cyrl"),
            ("Latin", "lat_Latn"),
            ("Luxembourgish", "ltz_Latn"),
            ("Lingala", "lin_Latn"),
            ("Lao", "lao_Laoo"),
            ("Lithuanian", "lit_Latn"),
            ("Latvian", "lvs_Latn"),
            ("Malagasy", "plt_Latn"),
            ("Maori", "mri_Latn"),
            ("Macedonian", "mkd_Cyrl"),
            ("Malayalam", "mal_Mlym"),
            ("Mongolian (Cyrillic)", "khk_Cyrl"),
            ("Marathi", "mar_Deva"),
            ("Malay", "zsm_Latn"),
            ("Maltese", "mlt_Latn"),
            ("Burmese", "mya_Mymr"),
            ("Norwegian Bokmål", "nob_Latn"),
            ("Nepali", "npi_Deva"),
            ("Dutch", "nld_Latn"),
            ("Norwegian Nynorsk", "nno_Latn"),
            ("Norwegian", "nor_Latn"),
            ("Occitan", "oci_Latn"),
            ("Oromo", "gaz_Latn"),
            ("Odia", "ory_Orya"),
            ("Punjabi", "pan_Guru"),
            ("Polish", "pol_Latn"),
            ("Pashto", "pbt_Arab"),
            ("Portuguese", "por_Latn"),
            ("Quechua", "que_Latn"),
            ("Romanian", "ron_Latn"),
            ("Russian", "rus_Cyrl"),
            ("Kinyarwanda", "kin_Latn"),
            ("Sanskrit", "san_Deva"),
            ("Sindhi", "snd_Arab"),
            ("Sinhala", "sin_Sinh"),
            ("Slovak", "slk_Latn"),
            ("Slovenian", "slv_Latn"),
            ("Samoan", "smo_Latn"),
            ("Shona", "sna_Latn"),
            ("Somali", "som_Latn"),
            ("Albanian", "sqi_Latn"),
            ("Serbian", "srp_Cyrl"),
            ("Swati", "ssw_Latn"),
            ("Southern Sotho", "sot_Latn"),
            ("Sundanese", "sun_Latn"),
            ("Swedish", "swe_Latn"),
            ("Swahili", "swh_Latn"),
            ("Tamil", "tam_Taml"),
            ("Telugu", "tel_Telu"),
            ("Tajik", "tgk_Cyrl"),
            ("Thai", "tha_Thai"),
            ("Tigrinya", "tir_Ethi"),
            ("Turkmen", "tuk_Latn"),
            ("Tagalog", "tgl_Latn"),
            ("Tswana", "tsn_Latn"),
            ("Tonga", "ton_Latn"),
            ("Turkish", "tur_Latn"),
            ("Tsonga", "tso_Latn"),
            ("Tatar", "tat_Cyrl"),
            ("Uyghur", "uig_Arab"),
            ("Ukrainian", "ukr_Cyrl"),
            ("Urdu", "urd_Arab"),
            ("Uzbek", "uzn_Latn"),
            ("Vietnamese", "vie_Latn"),
            ("Wolof", "wol_Latn"),
            ("Xhosa", "xho_Latn"),
            ("Yiddish", "ydd_Hebr"),
            ("Yoruba", "yor_Latn"),
            ("Chinese (Simplified)", "zho_Hans"),
            ("Zulu", "zul_Latn"),
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
                            ("العربية", "ar")
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