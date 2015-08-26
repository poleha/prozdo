def transliterate(text):
    text = text.lower()
    mapping = {
        'а': 'a',
        'б': 'b',
        'в': 'v',
        'г': 'g',
        'д': 'd',
        'е': 'e',
        'ё': 'e',
        'ж': 'zh',
        'з': 'z',
        'и': 'i',
        'й': 'i',
        'к': 'k',
        'л': 'l',
        'м': 'm',
        'н': 'n',
        'о': 'o',
        'п': 'p',
        'р': 'r',
        'с': 's',
        'т': 't',
        'у': 'u',
        'ф': 'f',
        'х': 'kh',
        'ц': 'ts',
        'ч': 'ch',
        'ш': 'sh',
        'щ': 'shch',
        'ь': '',
        'ъ': '',
        'ы': 'y',
        'э': 'e',
        'ю': 'iu',
        'я': 'ia',
    }

    res = ''
    for s in text:
        if s in mapping:
            s = mapping[s]
        res += s
    return res



def full_trim(text):
    text = text.replace(':', '_')
    text = text.replace('»', '_')
    text = text.replace('…', '_')
    text = text.replace('-', '_')
    text = text.replace('@', '_')
    text = text.replace(',', '_')
    text = text.replace('-', '_')
    text = text.replace('.', '_')
    text = text.replace('!', '_')
    text = text.replace('?', '_')
    text = text.replace('   ', '_')
    text = text.replace('  ', '_')
    text = text.replace(' ', '_')
    text = text.replace('(', '_')
    text = text.replace(')', '_')
    text = text.replace('/', '_')
    text = text.replace('[', '_')
    text = text.replace(']', '_')
    text = text.replace('»', '_')
    text = text.replace('"', '_')
    text = text.replace('_____', '_')
    text = text.replace('____', '_')
    text = text.replace('____', '_')
    text = text.replace('___', '_')
    text = text.replace('___', '_')
    text = text.replace('___', '_')
    text = text.replace('__', '_')
    text = text.replace('__', '_')
    text = text.replace('__', '_')
    text = text.replace('__', '_')
    text = text.replace('__', '_')
    text = text.replace('__', '_')
    text = text.replace('__', '_')
    text = text.replace('__', '_')
    text = text.replace('__', '_')
    text = text.replace('__', '_')
    return text

def make_alias(text):
    return transliterate(full_trim(text))



def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip