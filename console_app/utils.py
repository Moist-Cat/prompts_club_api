import unicodedata
import re

# shamelessly stolen
def slugify(value, allow_unicode=False):
    """
    Convert to ASCII if 'allow_unicode' is False. Convert spaces to hyphens.
    Remove characters that aren't alphanumerics, underscores, or hyphens.
    Convert to lowercase. Also strip leading and trailing whitespace.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value.lower()).strip()
    return re.sub(r'[-\s]+', '-', value)


def get_page(data):
    quantity = data['count']
    if data['next']:
        next = data['next'].split('/')[-1][-1]
    else:
        next = 'none'
    if data['previous']:
        previous = data['previous'].split('/')[-1][-1]
    else:
        previous = 'none'
    
    pages = {
            'total': quantity,
            'total_pages': int(quantity/5),
            'next': next,
            'previous': previous,
    }

    print('Enter to keep browsing, \"-1\" to stop, ' \
          'or any other number to continue')
    print(f'Total: {pages["total"]}')
    print(f'Total pages: {pages["total_pages"]}')
    print(f'Next: {pages["next"]}')
    print(f'Previous: {pages["previous"]}')
    
    return (input(), next)


def get_user_scenarios(app, username, page=''):
    raw_scenarios = app.get_object(f'account/{username}/content/{page}')
    for scenario in raw_scenarios['results']:
        raw_tags = app.get_object(f'scenario/{slugify(scenario["title"])}/tag')
        if raw_tags:
            print(raw_tags)
            tags = [tag['name'] for tag in raw_tags]
        else:
            tags = None
        print('---------------------')
        print(f'Created by: {user}')
        print(f'Title: {scenario["title"]}')
        print(f'Tags: {tags}')
        print(f'Description: {scenario["description"]}')
        print(f'Nsfw: {scenario["nsfw"]}')

    selection = get_page(scenarios)

    if not selection[0]:
        get_user_scenarios(selection[1])
    elif selection[0] == '-1':
        return
    else:
        get_user_scenarios(username, selection)
            
            
        
        
  
