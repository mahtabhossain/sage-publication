# this file contains a list of helper functions

import requests

'''
function to return the results of one page retrived through OpenAlex API matching the filter
argument:
    sage_id: the OpenAlex ID for SAGE publishing
    from_publication_date: either publication date (which is commented now) or publication_year
    endpoint: works [OpenAlex works Object]
    email: optional (an identifier who is retrieving through the API)
output:
    filtered_works_url: URL string for the API with complete filter
    results_page: the first response page
'''
def get_filtered_works_one_page(sage_id, from_publication_date, endpoint, email=None):
    filters = ",".join((
        'locations.source.publisher_lineage:{}'.format(sage_id),
        #'from_publication_date:{}'.format(from_publication_date),
        'publication_year:{}'.format(from_publication_date),
    ))

    # put the URL together
    filtered_works_url = 'https://api.openalex.org/{}?filter={}'.format(endpoint, filters)

    # if email is defined above
    if email:
        filtered_works_url += '&mailto={}'.format(email)

    response_text = requests.get(filtered_works_url)
    # check if the HTTP response code is 200? - not done at the moment
    # convert it to JSON object
    results_page = response_text.json()

    return filtered_works_url, results_page


'''
function to return a OpenAlex search query result
argument:
    sample_url: URL string of the search query
output:
    return the search query results
'''
def get_search_query_response(sample_url):
    response_text = requests.get(sample_url)
    results_page = response_text.json()
    return results_page


'''
function to return all the results retrived through OpenAlex API matching the filter
argument:
    filtered_works_url: URL string for the API with complete filter
output:
    return all the results that match the filter - looping through the retrieved results, each page contains 25 results
'''
def get_filtered_works_full(filtered_works_url):
    cursor = '*'

    select = ",".join((
        'id',
        'ids',
        'title',
        'display_name',
        'publication_year',
        'publication_date',
        'primary_location',
        'open_access',
        'authorships',
        'cited_by_count',
        'is_retracted',
        'is_paratext',
        'updated_date',
        'created_date',
    ))

    # loop through pages
    works = []
    loop_index = 0
    while cursor:
        # set cursor value and request page from OpenAlex
        url = f'{filtered_works_url}&select={select}&cursor={cursor}'
        page_with_results = requests.get(url).json()
    
        results = page_with_results['results']
        works.extend(results)

        # update cursor to meta.next_cursor
        cursor = page_with_results['meta']['next_cursor']
        loop_index += 1
        if loop_index in [25, 50, 100] or loop_index % 500 == 0:
            print(f'{loop_index} api requests made so far')
    
    print('{} api results made in total'.format(loop_index))
    return works

'''
    function to append API response inside a list to be insered inside pandas dataframe later
    argument:
        data: list to insert the data
        work: the work object of OpenAlex API
        work_open_access, work_open_access_status: open access related information of the work
        work_type: the location of the published work (journal, conference, etc.)
        author_id, author_name, author_position: author related information of the work
        institution_id, institution_name, institution_country_code, institution_type: author institution related information of the work
    output:
    
'''
def append_data(data, work, work_open_access=None, work_open_access_status=None, work_type=None, author_id=None, author_name=None, author_position=None, institution_id=None, institution_name=None, institution_country_code=None, institution_type=None):
    data.append({
        'work_id': work['id'],
        'work_title': work['title'],
        'work_display_name': work['display_name'],
        'work_publication_year': work['publication_year'],
        'work_publication_date': work['publication_date'],
        'work_open_access': work_open_access,
        'work_open_access_status': work_open_access_status,
        'work_type': work_type,
        #'work_apc_list': work_price,
        'author_id': author_id,
        'author_name': author_name,
        'author_position': author_position,
        'institution_id': institution_id,
        'institution_name': institution_name,
        'institution_country_code': institution_country_code,
        'institution_type': institution_type
    })
    return data