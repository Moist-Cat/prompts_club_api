import unicodedata
import re
import os
import sys

from manage import command
import post_data

def clear_screen(param_function):
    def inner_function(*args, **kwargs):
        os.system('clear')
        param_function(*args, **kwargs)
    return inner_function


# --- miscelanea ---
scen_snippets = ('Created by:',
                 'Title:',
                 'Rating:',
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
                   'Folders:')

separator = '---------------------'

header = '*********************\n'

# messages

browse_view_reminder = 'Remember you can always search for a particular ' \
          'scenario by adding a \"!\" plus the scenario '\
          'title. Or \"#\" plus a tag name to filter by a tag.'

make_review_message = {
                'value': 'So, final rating?: ',
                'review': 'Anithying to add?' \
                         '(this is not actually a question, ' \
                         'leving a comment is mandatory. ' \
                         'At least say \"based\" or something.: '}

perma_delete_warning = 'This action is permanent, '\
                'are you sure you want to proceed?' \
                '(Press Enter to cancel):'

wi_entry_input_warning = 'Entry(Be careful '\
                          'writing this one and ' \
                          'remember that pressing enter ' \
                          'is a no-no here): '

crud_commands_reminder = 'You can use add, edit or delete ' \
                         'commands here.'

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
            # this one is a lambda, since we can not 
            # let it be executed (since we pass it with arguments)
            go_back_funct = args[1]
            go_back_funct()
        except Exception as e:
            return
    elif type(selection[0]) == int:
        base_func(*fun_args, f'?page={selection[0]}')
    else:
        # since \"app\" is the first arg in 
        # every view
        command(fun_args[0], selection[0])

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
        children = app.get_object(f'account/folder/{name_slug}/children')['results']
        children_names = [child['name'] for child in children]
        children_names = ', '.join(children_names)
        params.extend([
              children_names
        ])
    print_item(*params, item=folder_snippets)

def show_folders(app, raw_folders):
    for folder in raw_folders['results']:
        show_folder(app, folder)

def show_scenario(app, raw_scenario, only_header=True):
    title_slug = slugify(raw_scenario['title'])
    tags = get_tags(app, f'scenario/{title_slug}')
    user = raw_scenario['user']
    username = app.get_object(f'account/{user}')
    average_rating = app.get_object(
                f'scenario/{title_slug}/ratings/average')

    if user and type(average_rating) != None:
        # cache
        params = [
                 username['username'],
                 raw_scenario['title'],
                 average_rating['average_rating'],
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
    """
    Urls for pages come like this:
    > https://site.com/api/thingy/?page=3
    
    We split it to get \"?page=3\" and we do it 
    again to get the page number (3, in this case).
    """
    
    quantity = data['count']
    if data['next'] and data['next'].split('/')[-1]:
        next = data['next'].split('/')[-1].split('=')[-1]
    else:
        next = ''
    if data['previous'] and data['previous'].split('/')[-1]:
        previous = data['previous'].split('/')[-1].split('=')[-1]
    else:
        previous = ''
    
    pages = {
            'total': quantity,
            'total_pages': int(quantity/10),
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
def view_wi(app, scenario_slug, page=''):
    print(f'SCENARIO WORLD INFO')
    print(header)

    raw_wi = app.get_object(f'scenario/{scenario_slug}/worldinfo/{page}')
    if raw_wi['results']:
        scenario_id = raw_wi['results'][0]['scenario']

        for wi in raw_wi['results']:
            print(separator)
            for k, v in wi.items():
                print(f'{k.capitalize()}: {v}')
        selection = get_page(raw_wi, crud_commands_reminder)

        if selection[0] == 'add':
            data = {
                    'scenario': scenario_id,
                    'keys': input('Keys: '),
                    'entry': input(wi_entry_input_warning)
            }
            app.create_object('scenario/worldinfo', data)
            
            view_scenario(app, scenario_slug)

        elif selection[0] == 'edit':
            data = {
                    'scenario': scenario_id,
                    'keys': input('Keys: '),
                    'entry': input(wi_entry_input_warning)
            }
            id = input("Wi ID: ")
            app.edit_object(f'scenario/worldinfo/{id}', data)
            
            view_scenario(app, scenario_slug)

        elif selection[0] == 'delete':
           id = input('WI ID: ')
           confirm = input(perma_delete_warning)
           if confirm:
               app.delete_object(f'scenario/worldinfo/{id}')
               
           view_scenario(app, scenario_slug)

        else:
            base_selection(
                    view_wi,
                    lambda:view_scenario(app, scenario_slug),
                    fun_args=[app, scenario_slug],
                    selection=selection
            )
    else:
        input('None found... press enter to go back.')
        view_scenario(app, scenario_slug)
        

@clear_screen
def view_ratings(app, scenario_slug, page=''):
    print(f'RATINGS FOR THIS SCENARIO')
    print(header)

    raw_ratings = app.get_object(f'scenario/{scenario_slug}/ratings/{page}')
    if raw_ratings['results']:
        scenario_id = raw_wi['results'][0]['scenario']

        for rating in raw_ratings['results']:
            for k, v in rating.items():
                if k != 'user':
                    print(f'{k.capitalize()}: {v}')
                else:
                    user = app.get_object(f'account/{v}')['username']
                    print('User:', user)

        selection = get_page(raw_ratings, crud_commands_reminder)


        if selection[0] == 'add':
            data = {
                    'user': 1,
                    'scenario': scenario_id,
                    'value': input(make_review_message['value']),
                    'review': input(make_review_message['review'])
            }
            app.create_object('scenario/rating', data)
            
            view_scenario(app, scenario_slug)

        elif selection[0] == 'edit':
            data = {
                    'user': 1,
                    'scenario': scenario_id,
                    'value': input(make_review_message['value']),
                    'review': input(make_review_message['review'])
            }
            id = input("Rating ID: ")
            app.edit_object(f'scenario/rating/{id}', data)
            
            view_scenario(app, scenario_slug)

        elif selection[0] == 'delete':
           id = input('Rating ID: ')
           confirm = input(perma_delete_warning)
           if confirm:
               app.delete_object(f'scenario/rating/{id}')
               
           view_scenario(app, scenario_slug)

        else:
            base_selection(
                    view_wi,
                    lambda:view_scenario(app, scenario_slug),
                    fun_args=[app, scenario_slug],
                    selection=selection
            )
    else:
        input('None found... press enter to go back.')
        view_scenario(app, scenario_slug)

@clear_screen
def view_users(app, page=''):
    print(f'USERS')
    print(header)

    raw_users = app.get_object(f'account')
    if raw_users:
        for user in raw_users['results']:
            print(separator)
            for k, v in user.items():
                print(f'{k.capitalize()}: {v}')

        selection = get_page(raw_users, '(XXX)')
        
        base_selection(
                view_users,
                fun_args=[app],
                selection=selection
        )

@clear_screen
def view_published_scenarios(app, page=''):
    print(f'PUBLIC SCENARIOS')
    print(header)

    raw_scenarios = app.get_object(f'scenario/{page}')
    if raw_scenarios:
        show_scenarios(app, raw_scenarios)
        
        selection = get_page(raw_scenarios)

        base_selection(
                view_published_scenarios,
                fun_args=[app],
                selection=selection
        )

@clear_screen
def view_tagged_scenarios(app, tag, page=''):
    print(f'SCENARIOS TAGGED WITH #{tag}')
    print(header)

    tag_slug = slugify(tag)
    raw_scenarios = app.get_object(f'scenario/tag/{tag_slug}/{page}')
    if raw_scenarios:
        show_scenarios(app, raw_scenarios)
        
        selection = get_page(raw_scenarios)

        base_selection(
                view_tagged_scenarios,
                lambda:view_published_scenarios(app),
                fun_args=[app, tag],
                selection=selection
        )

@clear_screen
def view_user_scenarios(app, username, page=''):
    print(f'{username}\'s SCENARIOS')
    print(header)

    raw_scenarios = app.get_object(f'account/{username}/content/{page}')
    if raw_scenarios:
        show_scenarios(app, raw_scenarios)

        selection = get_page(raw_scenarios)

        base_selection(
                view_user_scenarios,
                lambda:view_published_scenarios(app),
                fun_args=[app, username],
                selection=selection
        )

@clear_screen
def view_my_scenarios(app, page=''):
    print(f'MY SCENARIOS')
    print(header)
    
    raw_scenarios = app.get_object(f'scenario/mine')
    if raw_scenarios:
        show_scenarios(app, raw_scenarios)

        selection = get_page(raw_scenarios)

        base_selection(
                view_my_scenarios,
                lambda:view_published_scenarios(app),
                fun_args=[app],
                selection=selection
        )

@clear_screen
def view_my_tagged_scenarios(app, tag, page=''):
    print(f'MY SCENARIOS TAGGED WITH #{tag}')
    print(header)

    tag_slug = slugify(tag)
    raw_scenarios = app.get_object(f'scenario/tag/{tag_slug}/mine/{page}')
    if raw_scenarios:
        show_scenarios(app, raw_scenarios)
        
        selection = get_page(raw_scenarios)

        base_selection(
                view_my_tagged_scenarios,
                lambda:view_published_scenarios(app),
                fun_args=[app, tag],
                selection=selection
        )

@clear_screen
def view_scenario(app, scenario_title):
    print('SCENARIO DETAIL')
    print(header)

    title_slug = slugify(scenario_title)
    raw_scenario = app.get_object(f'scenario/{title_slug}')
    if raw_scenario:
        scenario_id = raw_scenario['id']
        show_scenario(app, raw_scenario, only_header=False)

        print('\nType \"w\" or \"r\" to see WI and ratings '\
              'for this scenario'\
              'You can also type \"user\"'\
              '(or \"u\") to see this user scenarios')
        selection = input('$ ')
        
        if selection.startswith('w'):
            view_wi(app, title_slug)

        elif selection == 'rate':
            data = {
                    'user': 1,
                    'scenario': scenario_id,
                    'value': input(make_review_message['value']),
                    'review': input(make_review_message['review'])
            }
            app.create_object(f'scenario/rating', data)
            view_scenario(app, scenario_title)

        elif selection.startswith('r'):
            view_ratings(app, title_slug)

        elif selection == 'add':
            data = {
                    'scenario': scenario_id,
                    'keys': input('Keys: '),
                    'entry': input(wi_entry_input_warning)
            }
            app.create_object(f'scenario/worldinfo', data)
            view_scenario(app, scenario_title)
            

        elif selection == '-1' or not selection:
            view_published_scenarios(app)

        else:
            command(app, selection)

def create_scenario(app):
    print('CREATE SCENARIO')
    print(header)

    # first, we see if the scenario is in a txt
    try:
        post_data.scenario_txt_with_wi_to_json()
    except FileNotFoundError:
        # it might be straigth a json
        pass

    # second, the .json file (scrapped by my/sa script, Mimi\'s AIDCAT 
    # should not work here since, her\'s does not group the 
    # scenarios like {"senarios": [...]} this). However, my fork 
    # should be fine.
    try:
        s = post_data.ScenarioOps(app)
        title = s.make_scenario()
        print(f'Your scenario \"{title}\" was successfully created')
        return
    except (FileNotFoundError, post_data.ScenarioExists):
         pass

def edit_scenario(app):
    print('EDIT SCENARIO')
    print(header)

    try:
        post_data.scenario_txt_with_wi_to_json()
    except FileNotFoundError:
        # it might be straight a json
        pass

    try:
        s = post_data.ScenarioOps(app)
        title = s.edit_scenario()
        print(f'Your scenario \"{title}\" was successfully edited')
        return
    except (FileNotFoundError, post_data.ScenarioExists) as e:
         print('Uh-oh... ', e)

def delete_scenario(app):
    print('DELETE SCENARIO')
    print(header)
    
    title = slugify(input('Scenario title: '))

    confirm = input(perma_delete_warning)
    
    if confirm:
        app.delete_object(f'scenario/{title}')

# folder views
@clear_screen
def view_user_folders(app, username, page=''):
    print(f'{username}\'s FOLDERS')
    print(header)

    raw_folders = app.get_object(f'account/{username}/folders')
    if raw_folders:
        show_folders(app, raw_folders)

        selection = get_page(raw_folders)

        base_selection(
                view_user_folders,
                lambda:view_public_folders(app),
                fun_args=[app, username],
                selection=selection
        )

@clear_screen
def view_public_folders(app, page=''):
    print('PUBLIC FOLDERS')
    print(header)

    raw_folders = app.get_object(f'account/folder/')
    if raw_folders:
        show_folders(app, raw_folders)

        selection = get_page(raw_folders)

        base_selection(
                view_public_folders,
                fun_args=[app],
                selection=selection
        )

@clear_screen
def view_tagged_folders(app, tag, page=''):
    print(f'FOLDERS TAGGED WITH #{tag}')
    print(header)

    tag_slug = slugify(tag)
    raw_folders = app.get_object(f'account/folder/tag/{tag_slug}')
    if raw_folders:
        show_folders(app, raw_folders)
    
        selection = get_page(raw_folders)

        base_selection(
                view_tagged_folders,
                lambda:view_public_folders(app),
                fun_args=[app, tag],
                selection=selection
        )

@clear_screen
def view_folder(app, folder_name, page=''):
    print('FOLDER DETAIL')
    print(header)


    name_slug = slugify(folder_name)
    raw_folder = app.get_object(f'account/folder/{name_slug}')
    if raw_folder:
        show_folder(app, raw_folder, only_header=False)
        folder_raw_scenarios = app.get_object(
                           f'account/folder/{name_slug}/scenarios/{page}'
                                )
        if folder_raw_scenarios:
            show_scenarios(app, folder_raw_scenarios)
        
            selection = get_page(folder_raw_scenarios,
                                 extra_message=('XXX')
                        )
            base_selection(
                    view_folder,
                    lambda:view_public_folders(app),
                    fun_args=[app, folder_name],
                    selection=selection
            )

@clear_screen
def view_my_tagged_folders(app, tag, page=''):
    print(f'FOLDERS TAGGED WITH #{tag}')
    print(header)

    tag_slug = slugify(tag)
    raw_folders = app.get_object(
              f'account/folder/tag/{tag_slug}/mine/{page}')
    if raw_folders:
        show_folders(app, raw_folders)
    
        selection = get_page(raw_folders)

        base_selection(
                view_my_tagged_folders,
                lambda:view_public_folders(app),
                fun_args=[app, tag],
                selection=selection
        )

@clear_screen
def view_my_folders(app, page=''):
    print(f'YOUR FOLDERS')
    print(header)

    raw_folders = app.get_object(f'account/folder/mine/{page}')
    if raw_folders:
        show_folders(app, raw_folders)

        selection = get_page(raw_folders)

        base_selection(
                view_my_folders,
                lambda:view_public_folders(app),
                fun_args=[app],
                selection=selection
        )


