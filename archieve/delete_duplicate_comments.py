#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "prozdo.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)

from main import models

from django.db import connection

cursor = connection.cursor()


cursor.execute("SELECT c.body, COUNT(c.id) FROM main_comment c GROUP BY c.body, c.post_id, c.user_id, c.session_key HAVING COUNT(c.id) > 1")
rows = cursor.fetchall()
for row in rows:
    print(row[1])
    comments = models.Comment.objects.filter(body=row[0])
    group = []
    for comment in comments:
        comment_weight = 0
        if comment.consult_done:
            comment_weight += 1
        if comment.available_children_count:
            comment_weight += 1
        if comment.confirmed:
            comment_weight += 0.5
        group.append((comment, comment_weight))

    max_weight = -1
    group_leader = None
    for comment, comment_weight in group:
        if comment_weight > max_weight:
            group_leader = comment
            max_weight = comment_weight
    print('leader', group_leader, max_weight)
    for comment, comment_weight in group:
        if not comment.pk == group_leader.pk:
            if comment_weight < 1:
                delete = True
            else:
                delete = False
            print('loser', comment, comment_weight, delete)
            if delete:
                comment.delete()




