import unicodedata
import re
import os
from manage import command

def clear_screen(param_function):
    def inner_function(*args, **kwargs):
        os.system('clear')
        param_function(*args, **kwargs)
    return inner_function


# --- miscelanea ---
scen_snippets = ('Created by:',
                 'Title:',
                 'Tags:',
                 'Description:',
                 'Nsfw:',
                 'Created:',
                 'Published:',
                 'Memory:',
                 'Authors Note:',
                 'Prompt:',
                 'Status:')

folder_snippets = ('User:',
                   'Name:',
                   'Description:',
                   'Tags:',
                   'Status:',
                   'Created:',
                   'Updated:',
                   'Folders:',
                   'Scenarios:')

separator = '---------------------'

browse_view_reminder = 'Remember you can always search for a particular ' \
          'scenario by adding a \"!\" plus the scenario '\
          'title. Or \"#\" plus a tag name to filter by a tag.'
    

# --- helpers ---
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


def base_selection(*args, **kwargs):
    """
    Takes 2 functions as parameters. The one who 
    is currently being executed and the one who will 
    execute if the user wants to go \"back\" with -1.
    Also receives the first function base args.
    """
    selection = kwargs['selection']
    base_func = args[0]
    fun_args = kwargs['fun_args']

    print(f'WHOOOOOOO {selection[0]} WHOOOOOOOOOOOO')

    try:
        selection[0] = int(selection[0])
    except ValueError:
        pass
    if not selection[0]:
        if selection[1]:
            base_func(*fun_args, f'?page={selection[1]}')
        else:
            base_func(*fun_args)
    elif selection[0] == -1:
        try:
            args[2]
        except:
            return
    elif type(selection[0]) == int:
        base_func(*fun_args, f'?page={selection[0]}')
    else:
        command(app, selection[0])

def print_item(*args, item=scen_snippets):
    print(separator)
    counter = 0
    for arg in args:
        print(item[counter], arg)
        counter+=1

def show_folder(app, raw_folder, only_header=True):
    name_slug = slugify(raw_folder['name'])
    tags = get_tags(app, f'account/folder/{name_slug}')
    user = raw_folder['user']
    username = app.get_object(f'account/{user}')['username']
    
    params = [
             username,
             raw_folder['name'],
             raw_folder['description'],
             tags,
             raw_folder['status'],
             raw_folder['created'],
             raw_folder['updated'],
    ]
    if not only_header:
        scenarios = get_object('account/folder/{name_slug}/scenarios')['results']
        scenario_titles = ', '.join([scenario['title'] for scenario in scenarios])
        children = get_object('account/folder/{name_slug}/children')['results']
        params.extend([
              children,
              scenario_titles,
    ])
    print_item(*params, item=folder_snippets)

def show_folders(app, raw_folders):
    for folder in raw_folders['results']:
        show_folder(app, folder)

def show_scenario(app, raw_scenario, only_header=True):
    title_slug = slugify(raw_scenario['title'])
    tags = get_tags(app, f'scenario/{title_slug}')
    user = raw_scenario['user']
    username = app.get_object(f'account/{user}')['username']

    params = [
             username,
             raw_scenario['title'],
             tags,
             raw_scenario['description'],
             raw_scenario['nsfw'],
             raw_scenario['created'],
             raw_scenario['publish']
    ]
    if not only_header:
        params.extend([
             raw_scenario['memory'],
             raw_scenario['authors_note'],
             raw_scenario['prompt'],
             raw_scenario['status']
        ])

    print_item(*params)

def show_scenarios(app, raw_scenarios):
    for scenario in raw_scenarios['results']:
        show_scenario(app, scenario)

def get_page(data, extra_message=browse_view_reminder):
    quantity = data['count']
    # urls for pages come like this:
    # > https://site.com/api/thingy/?page=3
    #
    # We slpit it to get ?page=3 and we do it 
    # again to get the page number.
    if data['next'] and data['next'].split('/')[-1]:
        next = data['next'].split('/')[-1].split('=')[-1]
    else:
        next = None
    if data['previous'] and data['previous'].split('/')[-1]:
        previous = data['previous'].split('/')[-1][-1]
    else:
        previous = None
    
    pages = {
            'total': quantity,
            'total_pages': int(quantity/5),
            'next': next,
            'previous': previous,
    }
    print('\n#####################\n')
    print(f'Total: {pages["total"]}')
    print(f'Total pages: {pages["total_pages"]}')
    print(f'Next: {pages["next"]}')
    print(f'Previous: {pages["previous"]}')
    print('Enter to keep browsing, \"-1\" go back, ' \
          'or any other number to continue.')
    print(extra_message)
    return [input('$'), next]

def get_tags(app, obj_url):
    raw_tags = app.get_object(f'{obj_url}/tag')
    if raw_tags:
        tags = [tag['name'] for tag in raw_tags['results']]
        return ', '.join(tags)
    else:
        return None

# --- views ---
@clear_screen
def get_wi(app, scenario_slug, page=''):
    raw_wi = app.get_object(f'scenario/{scenario_slug}/worldinfo/{page}')
    if raw_wi['results']:
        for wi in raw_wi['results']:
            print(separator)
            for k, v in wi.items():
                print(f'{k.capitalize()}: {v}')
        selection = get_page(raw_wi, '(XXX)')

        base_selection(
                get_wi,
                get_scenario(app, scenario_slug),
                fun_args=[app, scenario_slug],
                selection=selection
        )

@clear_screen
def get_ratings(app, scenario_slug, page=''):
    raw_ratings = app.get_object(f'scenario/{scenario_slug}/ratings/{page}')
    if raw_ratings['results']:
        for rating in raw_ratings['results']:
            for k, v in rating.items():
                if k != 'user':
                    print(f'{k.capitalize()}: {v}')
                else:
                    user = get_object(f'account/{v}')['username']
                    print('User:', user)
        selection = get_page(raw_ratings, '(XXX)')


        base_selection(
                get_ratings,
                get_scenario(app, scenario_slug),
                fun_args=[app, scenario_slug],
                selection=selection
        )

@clear_screen
def get_users(app, page=''):
    raw_users = app.get_object(f'account')
    if raw_users:
        for user in raw_users['results']:
            print(separator)
            for k, v in user.items():
                print(f'{k.capitalize()}: {v}')

        selection = get_page(raw_users, '(XXX)')
        
        base_selection(
                get_users,
                fun_args=[app],
                selection=selection
        )

@clear_screen
def get_published_scenarios(app, page=''):
    raw_scenarios = app.get_object(f'scenario/{page}')
    if raw_scenarios:
        show_scenarios(app, raw_scenarios)
        
        selection = get_page(raw_scenarios)

        base_selection(
                get_published_scenarios,
                fun_args=[app],
                selection=selection
        )

@clear_screen
def get_tagged_scenarios(app, tag, page=''):
    tag_slug = slugify(tag)
    raw_scenarios = app.get_object(f'scenario/tag/{tag_slug}/{page}')
    if raw_scenarios:
        show_scenarios(app, raw_scenarios)
        
        selection = get_page(raw_scenarios)

        base_selection(
                get_tagged_scenarios,
                get_published_scenarios(app),
                fun_args=[app, tag],
                selection=selection
        )

@clear_screen
def get_user_scenarios(app, username, page=''):
    raw_scenarios = app.get_object(f'account/{username}/content/{page}')
    if raw_scenarios:
        show_scenarios(app, raw_scenarios)

        selection = get_page(raw_scenarios)

        base_selection(
                get_user_scenarios,
                get_published_scenarios(app),
                fun_args=[app, username],
                selection=selection
        )

@clear_screen
def get_scenario(app, scenario_title):
    title_slug = slugify(scenario_title)
    raw_scenario = app.get_object(f'scenario/{title_slug}')
    if raw_scenario:
        show_scenario(app, raw_scenario, only_header=False)

        selection = input('\nType \"w\" or \"r\" to see WI and ratings '\
                          'for this scenario'\
                          'You can also type \"user\"'\
                          '(or \"u\") to see this user scenarios\n$')
        if selection.startswith('w'):
            get_wi(app, title_slug)
        elif selection.startswith('r'):
            get_ratings(app, title_slug)
        elif selection == '-1':
            get_published_scenarios(app)
        else:
            command(app, selection)

@clear_screen
def get_user_folders(app, username, page=''):
    raw_folders = app.get_object(f'account/{username}/folders')
    if raw_folders:
        show_folders(app, raw_folders)

        selection = get_page(raw_folders)

        base_selection(
                get_user_folders,
                get_public_folders(app),
                fun_args=[app, username],
                selection=selection
        )

@clear_screen
def get_public_folders(app, page=''):
    raw_folders = app.get_object(f'account/folder/')
    if raw_folders:
        show_folders(app, raw_folders)

        selection = get_page(raw_folders)

        base_selection(
                get_public_folders,
                fun_args=[app],
                selection=selection
        )

@clear_screen
def get_tagged_folders(app, tag, page=''):
    tag_slug = slugify(tag)
    raw_folders = app.get_object(f'account/folder/{tag_slug}')
    if raw_folders:
        show_folders(app, raw_folders)
    
        selection = get_page(raw_folders)

        base_selection(
                get_tagged_folders,
                get_public_folders(app),
                fun_args=[app, tag],
                selection=selection
        )
