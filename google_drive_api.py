# -*- coding: utf-8 -*-

from apiclient import errors
from apiclient.http import MediaIoBaseUpload
import os

GOOGLE_DOC_MIME_TYPE = 'application/vnd.google-apps.document'
DOCX_MIME_TYPE = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
FOLDER_MIME_TYPE = 'application/vnd.google-apps.folder'
LOCAL_SHARE_CLASS_FOLDER_ID = "0B8EoFMWDwomTWnFpUzFXdnRTeFU"
SERVER_SHARE_CLASS_FOLDER_ID = "0B-kp5lphrPvDV21zcnM3Yl9kRVE"
IS_DEV_SERVER = (os.environ.get('SERVER_SOFTWARE', '').startswith('Development')
                     and not os.environ.get('FAKE_PROD_APPSERVER'))
if IS_DEV_SERVER:
    ROOT_FOLDER_ID = LOCAL_SHARE_CLASS_FOLDER_ID
else:
    ROOT_FOLDER_ID = SERVER_SHARE_CLASS_FOLDER_ID


def get_file_info(service, file_id):
  """Return file info

  Args:
    service: Drive API service instance.
    file_id: ID of the file to print metadata for.
  """
  try:
    file = service.files().get(fileId=file_id).execute()
    return file

  except errors.HttpError, error:
    print 'An error occurred: %s' % error


def insert_file(service, title, filecontent, mime_type, parent_id=ROOT_FOLDER_ID):
  """Insert new file.

  Args:
    service: Drive API service instance.
    title: Title of the file to insert, including the extension.
    description: Description of the file to insert.
    parent_id: Parent folder's ID.
    mime_type: MIME type of the file to insert.
    filename: Filename of the file to insert.
  Returns:
    Inserted file metadata if successful, None otherwise.
  """
  media_body = MediaIoBaseUpload(filecontent, mimetype=mime_type, resumable=True)
  body = {
    'title': title,
    'mimeType': mime_type
  }
  # Set the parent folder.
  if parent_id:
    body['parents'] = [{'id': parent_id}]

  try:
    file = service.files().insert(
        body=body,
        media_body=media_body,
        convert=True).execute()

    # Uncomment the following line to print the File ID
    # print 'File ID: %s' % file['id']

    return file
  except errors.HttpError, error:
    print 'An error occured: %s' % error
    return None


def update_file(service, file_id, filecontent, mime_type):
  """Insert new file.

  Args:
    service: Drive API service instance.
    title: Title of the file to insert, including the extension.
    description: Description of the file to insert.
    parent_id: Parent folder's ID.
    mime_type: MIME type of the file to insert.
    filename: Filename of the file to insert.
  Returns:
    Inserted file metadata if successful, None otherwise.
  """
  media_body = MediaIoBaseUpload(filecontent, mimetype=mime_type, resumable=True)
  try:
    file = service.files().update(
        fileId=file_id,
        media_body=media_body,
        newRevision=True,
        ).execute()

    # Uncomment the following line to print the File ID
    # print 'File ID: %s' % file['id']

    return file
  except errors.HttpError, error:
    print 'An error occured: %s' % error
    return None


def insert_folder(service, title, parent_id):
  """Insert new folder.

  Args:
    service: Drive API service instance.
    title: Title of the file to insert, including the extension.
    parent_id: Parent folder's ID.
  Returns:
    Inserted folder metadata if successful, None otherwise.
  """

  body = {
    'title': title,
    'mimeType': FOLDER_MIME_TYPE
  }
  # Set the parent folder.
  if parent_id:
    body['parents'] = [{'id': parent_id}]

  try:
    file = service.files().insert(
        body=body).execute()

    # Uncomment the following line to print the File ID
    # print 'File ID: %s' % file['id']

    return file
  except errors.HttpError, error:
    print 'An error occured: %s' % error
    return None

def insert_permission(service, file_id, value, perm_type, role):
  """Insert a new permission.

  Args:
    service: Drive API service instance.
    file_id: ID of the file to insert permission for.
    value: User or group e-mail address, domain name or None for 'default'
           type.
    perm_type: The value 'user', 'group', 'domain' or 'default'.
    role: The value 'owner', 'writer' or 'reader'.
  Returns:
    The inserted permission if successful, None otherwise.
  """
  new_permission = {
      'value': value,
      'type': perm_type,
      'role': role
  }
  try:
    return service.permissions().insert(
        fileId=file_id, body=new_permission).execute()
  except errors.HttpError, error:
    print 'An error occurred: %s' % error
  return None


''' show things inside the folder 
    results = service.files().list(maxResults=20).execute()
    items = results.get('items', [])
    if not items:
        logging.info('No files found.')
    else:
        logging.info('Files:')
        for item in items:
            logging.info(item['title']+'   '+item['id'])
'''

# 讓可以上傳檔案 並轉換成 google doc form：
# google_drive_api.insert_file(service, 'myword123321', 'test for docx file', '0BwWPcLB3G5fncHlkVi1feEstV00', 'myword222.docx')

# 讓可以創造一個資料夾：
# google_drive_api.insert_folder(service, 'share-course', 'root')


# 讓可以給別的使用者權限：
# google_drive_api.insert_permission(service, '0BwWPcLB3G5fncHlkVi1feEstV00', 'fonyou1337@gmail.com', 'user', 'writer')

# 可以給所有的使用者 read 權限
# google_drive_api.insert_permission(service, '0BwWPcLB3G5fncHlkVi1feEstV00', '', 'anyone', 'reader')

# 讓可以下載檔案
# get.exportLinks['application/vnd.openxmlformats-officedocument.wordprocessingml.document']

# 讓可以預覽檔案 用下面這個iframe 即可預覽
# <iframe src="https://docs.google.com/viewer?url=https://docs.google.com/document/d/{{file id}}/export?format%3Dpdf&embedded=true" style="width:400px; height:560px;" frameborder="0"></iframe>

# 讓可以線上編輯檔案、給 Comment
# get.defaultOpenWithLink
