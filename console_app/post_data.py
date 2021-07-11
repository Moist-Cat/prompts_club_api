import json
import views

class ScenarioExists(Exception):
    pass

class ScenarioDoesNotExist(Exception):
    pass

def scenario_txt_to_json(data_file='scenario.txt'):
    scen_data = {'scenarios' : [{
                                'user': 1,
                                'title': '',
                                'tags': '',
                                'description': '',
                                'prompt': '',
                                'memory': '',
                                'authorsNote': '',
                                'nsfw': '',
                                'status': ''
            }]
    }

    required_data = ('title', 'tags', 'description', 'prompt',
                     'memory','authorsNote', 'nsfw','status')

    file = open(data_file)
    counter = -1
    for line in file:
       if not line.startswith('#'):
           if not required_data[counter] == 'tags':
               scen_data['scenarios'][0][required_data[counter]] += line
           elif line != '\n':
               # We have the tags
               tags = line.strip().split(', ')
       else:
           # get rid of unnecessary spaces
           scen_data['scenarios'][0][required_data[counter]] = \
               scen_data['scenarios'][0][required_data[counter]].strip()
           counter+=1

    scen_data['scenarios'][0]['status'] = \
       scen_data['scenarios'][0]['status'].strip()
    file.close()

    scen_data['scenarios'][0].update({'tags': tags})

    return scen_data

def worldinfo_txt_to_json(data_file='worldinfo.txt'):
    with open(data_file) as file:
        data = file.read()
    world_info = {'worldInfo': []}
    wi = {
         'keys': '',
         'entry': ''
         }
    raw_world_info = data.split('\n')
    try:
        while True:
            raw_world_info.remove('')
    except:
        pass
    
    hash_counter = 0
    for item in raw_world_info:
        if item.startswith('#'):
            hash_counter+=1
            continue
        else:
            if hash_counter % 2:
                # Keys, since those go first. We have 
                # one "#" form the first line
                if wi['keys']:
                    # if there is data written, it means a WI was 
                    # already there, so we append it before overwritting 
                    # it with the next one.
                    world_info['worldInfo'].append(wi)
                    wi = {'keys':'', 'entry': ''}
                wi['keys'] = item.strip()
            else:
                # Entry, we have our WI now.
                wi['entry'] += item.strip()
        if raw_world_info[-1] == item:
            # the last one needs to be added manually.
            world_info['worldInfo'].append(wi)
    
    return world_info

def scenario_txt_with_wi_to_json():
    # Add the WI
    scen_data = scenario_txt_to_json()
    try:
        world_info = worldinfo_txt_to_json()
    except FileNotFoundError:
        # No need to force people into adding wi.
        world_info = {'worldInfo': []}

    scen_data['scenarios'][0].update(world_info)
    with open('stories.json', 'w') as file:
        json.dump(scen_data, file)

class ScenarioOps:
    def __init__(self, app):
        self.app = app
        self.GET = app.get_object
        self.MAKE = app.create_object
        self.UPDATE = app.edit_object
        self.DELETE = app.delete_object

    def load_scenario_from_json(self, json_file='stories.json'):
        with open(json_file) as file:
            try:
                scenario = json.load(file)['scenarios'][0]
            except KeyError:
                # *tsk*
                scenario = json.load(file)[0]
        
        return scenario

    def format_scenario_data(self, scenario):
        try:
            status = scenario['status']
            nsfw = scenario['nsfw']
        except KeyError:
            status = 'draft'
            nsfw = False
            for tag in scenario['tags']:
                if tag == 'nsfw':
                    nsfw = True

        scen_data = {
                'user': scenario['user'],
                'title': scenario['title'],
                'description': scenario['description'],
                'prompt': scenario['prompt'],
                'memory': scenario['memory'],
                'authors_note': scenario['authorsNote'],
                'status': status,
                'nsfw': nsfw
        }
        
        return scen_data

    def add_when_called(self):
        item_number = 0
        while True:
            yield item_number
            item_number += 1

    def get_scenario_attr_id(self, title_slug, attr_name, lookup_field):
        data = {}
        pages = 1
        items = self.add_when_called()
        while True:
            res = self.GET(f'scenario/{title_slug}/' \
                           f'{attr_name}/?page={pages}')
            
            if not res:
                break
            
            # black magic here. We use a filed
            # to get the id, that (should) 
            # be unique for each scenario.
            #
            # counter added to the items since the "field" could 
            # have been edited
            # I need to find another way to do this...
            page = {item[lookup_field]: (item['id'], next(items)) for item in res['results']}
            print(page)
            data.update(page)
            pages += 1
        return data

    # CRUD
    def make_scenario(self):
        scenario = self.load_scenario_from_json()
        scen_data = self.format_scenario_data(scenario)

        res = self.MAKE('scenario', data=scen_data)
        if res:
            scen_id = res['id']
        else:
            raise ScenarioExists

        if scenario['worldInfo']:
            for wi in scenario['worldInfo']:
                wi_data = {
                           'scenario': scen_id,
                           'keys': wi['keys'],
                           'entry': wi['entry']
                }
                self.MAKE('scenario/worldinfo', wi_data)
        if scenario['tags']:
            for tag in scenario['tags']:
                tag_data = {
                    'scenario': scen_id,
                    'name': tag,
                    'slug': views.slugify(tag)
                }
                self.MAKE(
                     f'scenario/{views.slugify(scenario["title"])}/tag',
                     tag_data)
        return scenario['title']
    
    def edit_scenario(self):
        scenario = self.load_scenario_from_json()
        scen_data = self.format_scenario_data(scenario)

        title_slug = views.slugify(scenario['title'])
        res = self.UPDATE(f'scenario/{title_slug}', scen_data)

        if res:
            scen_id = res['id']
        else:
            raise ScenarioDoesNotExist

        counter = 0
        if scenario['worldInfo']:
            IDS = self.get_scenario_attr_id(title_slug,
                                            'worldinfo',
                                            'keys')
            
            for wi in scenario['worldInfo']:
                wi_data = {
                           'scenario': scen_id,
                           'keys': wi['keys'],
                           'entry': wi['entry']
                }
                try:
                    pk = IDS[wi_data['keys'][0]]
                    print(pk)
                except KeyError as e:
                    # get the id based on how many WI entries there are 
                    # worth a shot...
                    pk = [v[0] for k, v in IDS.items() if v[1] == counter][0]
                self.UPDATE(f'scenario/worldinfo/{pk}', wi_data)
                counter += 1

        if scenario['tags']:
            # get the old tags
            tags = self.GET(f'scenario/{title_slug}/tag')['results']
            tags_ids = {tag['name']: tag['id'] for tag in tags}

            old_tags = {tag['name'] for tag in tags}
            new_tags = {tag for tag in scenario['tags']}
            
            deleted_tags = old_tags.difference(new_tags)
            added_tags = new_tags.difference(old_tags)

            if added_tags:
                for tag in added_tags:
                    tag_data = {
                        'scenario': scen_id,
                        'name': tag,
                        'slug': views.slugify(tag)
                    }
                    self.MAKE(
                         f'scenario/{title_slug}/tag',
                         tag_data)

            if deleted_tags:
                for tag in deleted_tags:
                    id = tags_ids[tag]
                    self.DELETE(
                        f'scenario/{title_slug}/tag/{id}')

        return scenario['title']
