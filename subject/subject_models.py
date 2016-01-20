from google.appengine.ext import ndb
import logging


class Subject(ndb.Model):  # work as nodes in tree
    """The model class for product subject information. Supports building a
    subject tree."""

    parent_key = ndb.KeyProperty()
    level = ndb.IntegerProperty(default=0, required=True)
    name = ndb.StringProperty(default="", required=True)
    children = ndb.KeyProperty(repeated=True)

    @classmethod
    def buildSubjectTree(cls, subject_data, parent_key=None, level=0, order=0):
        """build a subject and any children from the given data dict."""

        if not subject_data:
            return

        sname = subject_data.get('name')
        if not sname:
            logging.warn('no subject name for %s', subject_data)
            return

        subject = cls(name=sname, parent_key=parent_key, level=level)
        subject.put()

        children = subject_data.get('children')
        children_list = []
        # if there are any children, build them using their parent key
        if children is not None:
            for child in children:
                child_subject = cls.buildSubjectTree(child, parent_key=subject.key, level=level+1)
                children_list.append(child_subject.key)
        subject.children = children_list
        subject.put()

        return subject

    def getParentSubject(self):
        return self.parent_key.get()

    def getChildrenSubjects(self):
        return [child_key.get() for child_key in self.children]

    def getSubjectTreeDict(self):
        subject_dict = {'id': self.key.id(), 'children': [], 'name': self.name, 'level': self.level}
        for child in self.getChildrenSubjects():
            subject_dict['children'].append(child.getSubjectTreeDict())
        return subject_dict
