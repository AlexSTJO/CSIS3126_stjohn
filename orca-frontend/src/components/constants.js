/// const BASE_URL = "https://astjo.site/api";
const BASE_URL = "http://127.0.0.1:5000"
export const API_ENDPOINTS = {
  REGISTER: `${BASE_URL}/register`,
  LOGIN: `${BASE_URL}/login`,
  UPLOAD_CREDENTIALS: `${BASE_URL}/upload-credentials`,
  GET_ACCOUNT_INFO: `${BASE_URL}/get-account-info`,
  CREDENTIAL_RESET: `${BASE_URL}/credential-reset`,
  PERMISSIONS_CHECK: `${BASE_URL}/permissions-check`,
  RESOURCE_STATUS: `${BASE_URL}/check-resource-existence`,
  RESOURCE_CREATE: `${BASE_URL}/create-resource`,
  LIST_PROJECTS: `${BASE_URL}/list-projects`,
  GET_PROJECT_TASKS: `${BASE_URL}/get-project-tasks/`,
  EDIT_TASK: `${BASE_URL}/edit-task`,
  ADD_TASK: `${BASE_URL}/add-task`,
  REMOVE_TASK: `${BASE_URL}/remove-task`
}
