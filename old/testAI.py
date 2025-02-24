import spacy

# Load the pre-trained spaCy model
nlp = spacy.load("en_core_web_sm")

def extract_address_with_spacy(message):
    doc = nlp(message)
    addresses = [ent.text for ent in doc.ents if len(ent.text) == 44]  # Detect 43-char address
    return addresses

message = """
🚨HIGH RISK HIGH REWARD GAMBLE PLAY🚨

GOING OUT ACROSS ALL PLATFORMS

GOOD NARRATIVE FART META. THE ONLY OTHER FART BOOK MY ADAM WALLACE LIKE THE FARTBOY COIN  THAT RAN OVER 200M THE REST ARE JUST DERIVATIVES EXCEPT THIS ONE SO I THINK ITS SUPER UNDERVALUED. 300K MC AREA DYOR NFA.

https://dexscreenerKING.com/solana/4iWpF4TMzHnDP7tjfYWqW8x1qWHb1AbqNhhJqVdTYxL4

https://fartclubsol.com/

https://x.com/fartclub_cto

https://t.me/cto_fartclub

6zkZPeSVSynKKINGoNgPjb6yCfJ5BFFro4gcKXuMrPtvpump

YOU HAVE TO REMOVE THE WORD “KING” FROM THE CA AND DEX LINK SO BOTS GET SIDELINED
"""
print(extract_address_with_spacy(message))