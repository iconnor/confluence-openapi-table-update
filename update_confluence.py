import os
import json
import requests
import argparse
from atlassian import Confluence
from markdown import markdown

def endpoint_content(method_dict):
    # Add any parameters to the endpoint (first with ? then with &)
    endpoint = ""
    if "parameters" in method_dict:
        for parameter in method_dict["parameters"]:
            if ("required" in parameter) and (parameter["required"] == True):
                if "?" in endpoint:
                    endpoint += "&amp;"
                else:
                    endpoint += "?"
                    endpoint += parameter["name"] + "={" + parameter["name"] + "}"
    return endpoint

def parameters_content(parameters_dict):
    parameters = ""
    for parameter in parameters_dict:
        field_name = parameter['name']
        if parameter.get("required") == False:
            field_name += " (optional)"
        if "description" in parameter:
            description = markdown(parameter['description'])
            # Insert field name after the opening <p> tag
            parameters += description.replace("<p>", f"<p><strong>{field_name}</strong>: ", 1)
    return parameters

def schema_to_example(schema):
    # given a schema return a json formatted example string
    if "properties" in schema:
        code_block = json.dumps(schema["properties"], indent=4, sort_keys=True)
        return f"""<ac:structured-macro ac:name="code">
                <ac:parameter ac:name="language">json</ac:parameter>
                <ac:plain-text-body><![CDATA[{code_block}]]></ac:plain-text-body>
                </ac:structured-macro>"""
    else:
        return ""
    

def responses_content(responses_dict):
    responses = ""
    for code in responses_dict:
        response = responses_dict[code]
        if "description" in response:
            responses_content = markdown(response['description'])
            # Insert field name after the opening <p> tag
            responses_content = responses_content.replace("<p>", f"<p><strong>{code}</strong>: ", 1)
            if "content" in response:
                body_schema = schema_to_example(response['content']['application/json']['schema'])
                if body_schema:
                    responses_content = responses_content.replace("</p>", f"</p><p><strong>Body</strong><br />{body_schema}</p>", -1)
            responses += responses_content
    return responses

def openapi_to_html(open_api_json_url):
    # load json from the url
    response = requests.get(open_api_json_url)
    data = response.json()
    
    # create table header
    html = "<table data-layout='full-width'>"
    html += "<tr>"
    html += "<th><strong>Endpoint</strong></th>"
    html += "<th><strong>Attributes</strong></th>"
    html += "<th><strong>Method</strong></th>"
    html += "<th><strong>Description</strong></th>"
    html += "<th><strong>Responses</strong></th>"
    html += "</tr>"

    # loop through json data
    for path in data["paths"]:
        for method in data["paths"][path]:
            
            html += "<tr>"
            endpoint = endpoint_content(data["paths"][path][method])
            html += "<td>{}/{}</td>".format(path, endpoint)
            if "parameters" in data["paths"][path][method]:
                html += "<td>{}</td>".format(parameters_content(data["paths"][path][method]["parameters"]))
            else:
                html += "<td></td>"
            html += "<td>{}</td>".format(method.upper())
            if "description" in data["paths"][path][method]:
                html += "<td>{}</td>".format(data["paths"][path][method]["description"])
            else:
                html += "<td></td>"
            if "responses" in data["paths"][path][method]:
                html += "<td>{}</td>".format(responses_content(data["paths"][path][method]["responses"]))
            else:
                html += "<td></td>"
            html += "</tr>"

    # close table
    html += "</table>"

    return html

def main():
    parser = argparse.ArgumentParser(
        description='Update Confluence page with OpenAPI table')

    parser.add_argument('--open-api-json-url', required=False,
                        help='OpenAPI json url', default='http://localhost:8080/v3/api-docs')
    parser.add_argument('--confluence-url', required=False,
                        help='Confluence url', default=os.getenv('CONFLUENCE_URL'))
    parser.add_argument('--confluence-email', required=False,
                        help='Confluence email', default=os.getenv('JIRA_EMAIL'))
    parser.add_argument('--confluence-token', required=False,
                        help='Confluence personal API token', default=os.getenv('JIRA_TOKEN'))
    parser.add_argument('--confluence-space', required=False,
                        help='Confluence space', default='LEAD')
    parser.add_argument('--confluence-page-title', required=False,
                        help='Confluence page title', default='API Page')
    parser.add_argument('--confluence-page-insertion-tag', required=False,
                        help='Confluence page insertion tag (table will replace table after this tag)', default='<h4>Endpoints')
    

    args = parser.parse_args()
    # Get the openapi json url from the environment
    url = args.confluence_url
    email = args.confluence_email
    api_key = args.confluence_token
    space = args.confluence_space
    # Connect to confluence
    confluence = Confluence(url, email, api_key)
    # Get the page id for the page we want to update
    page_id = confluence.get_page_id(space, args.confluence_page_title)

    if page_id is None:
        print("Page not found")
        return

    body = openapi_to_html(args.open_api_json_url)

    # Get the page content
    page = confluence.get_page_by_id(page_id, expand='body.storage')

    # Find the heading before the table
    heading_start = page['body']['storage']['value'].find(args.confluence_page_insertion_tag)

    # Find the table in the page content after the heading
    table_start = page['body']['storage']['value'].find('<table', heading_start)
    table_end = page['body']['storage']['value'].find('</table>', table_start) + 8

    # Replace the table with the new content
    page['body']['storage']['value'] = page['body']['storage']['value'][:table_start] + body + page['body']['storage']['value'][table_end:]

    # Update the page with the new content
    print("Updating page", page_id, args.confluence_page_title)
    
    print(page)
    ret = confluence.update_page(
        page_id=page_id,
        title=args.confluence_page_title,
        body=page['body']['storage']['value'],
        type='page',
        always_update=True
    )

    # Report if the update was successful
    if ret['id'] == page_id:
        print("Page updated successfully")
    else:
        print("Page update failed", ret)
        
if __name__ == "__main__":
    main()