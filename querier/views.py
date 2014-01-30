import json
from django.http import HttpResponse
from django.db import connection, DatabaseError
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt


def make_query(sql_query):
    cursor = connection.cursor()
    try:
        cursor.execute(sql_query)
        output_string = render_to_string('query_result.html', 
                                         { 'headers': [col[0] for col in cursor.description],
                                           'rows': cursor.fetchall() })
    except DatabaseError as exc:
        output_string = render_to_string('error_page.html', 
                                         { 'query': sql_query,
                                           'message': exc[1] })
    return output_string


def query(request):
    return HttpResponse(make_query(request.GET.get('query','')))


@csrf_exempt
def xqueue_interface(request):
    try:
        content = json.loads(request.body)
        body = json.loads(content['xqueue_body'])
        student_response = body['student_response']
        query_output = make_query(student_response)
        response_dict = {'correct': True,
                         'score': 1,
                         'msg': query_output}
        return HttpResponse(json.dumps(response_dict))
    except (ValueError, KeyError):
        return HttpResponse("The request was improperly formatted.  Please contact support.", status=500)
    
