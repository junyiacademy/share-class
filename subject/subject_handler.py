# -*- coding: utf-8 -*-

from handlers import BaseHandler
from user_data.user_models import UserData
from subject_models import Subject
import json
import logging


class UploadSubjectTree(BaseHandler):

    def get(self):

        user = UserData.get_current_user()
        if not user.is_server_admin():
            self.redirect('find-course')

        root_subjects = Subject.getSubjectByLevel(0)
        data = {
            'root_subjects': root_subjects
        }

        self.render('admin/upload-subject-tree.html', data)

    def post(self):

        def append_node_to_tree(node_list, tree):  # tree is empty list at first
            cursor = tree
            for index, value in enumerate(node_list):
                if value in [c['name'] for c in cursor]:
                    cursor = cursor[[c['name'] for c in cursor].index(value)]['children']
                else:
                    if index+1 != len(node_list):
                        cursor.append({'name': value, 'children': []})
                        cursor = cursor[-1]['children']
                    else:
                        cursor.append({'name': value})

        user = UserData.get_current_user()
        if not user.is_server_admin():
            self.redirect('find-course')

        csv_file = self.request.get("subject-tree-csv")
        logging.info('csv file : %s' % csv_file)

        tree = []
        if csv_file:
            for line in csv_file.splitlines():
                append_node_to_tree(line.split(','), tree)

        logging.info("tree: %s" % tree)
        if len(tree) > 1:
            self.render_json({"error": "系統目前不支援同時上傳多個科目，換句話說，您上傳的csv的第一行名稱需要全部相同。"})
            return

        root_subject = Subject.buildSubjectTree(tree[0])
        tree[0]['root_subject_id'] = root_subject.key.id()
        self.render_json(tree[0])

        return


class DeleteSubjectTree(BaseHandler):

    def post(self, subject_id):

        logging.info("INTO DELETESUBJECTTREE HANDLER!!")

        to_be_deleted = Subject.get_by_id(int(subject_id))
        deleted_name = to_be_deleted.name
        to_be_deleted.deleteSubjectRecursive()

        self.render_json({"msg": "成功刪除科目%s, 還有一切以下的子科目。" % deleted_name})
        return
