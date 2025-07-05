//@ts-check
import axios from "axios";

export default class SACApi {
  constructor(baseURL, authToken) {
    this.axiosInstance = axios.create({
      baseURL,
      headers: {
        Authorization: `Token ${authToken}`,
        "Content-Type": "application/json",
      },
    });

    this.permissions = new Permissions(this.axiosInstance);
    this.privileges = new Privileges(this.axiosInstance);
    this.roles = new Roles(this.axiosInstance);
    this.servers = new Servers(this.axiosInstance);
    this.serverPrivileges = new ServerPrivileges(this.axiosInstance);
    this.webhookLogs = new WebhookLogs(this.axiosInstance);
    this.rotations = new Rotations(this.axiosInstance);
  }
}

class Permissions {
  constructor(axiosInstance) {
    this.axios = axiosInstance;
  }

  list(params = {}) {
    return this.axios.get("/v1/api/privileged/permissions/", { params });
  }

  create(data) {
    return this.axios.post("/v1/api/privileged/permissions/", data);
  }

  retrieve(id) {
    return this.axios.get(`/v1/api/privileged/permissions/${id}/`);
  }

  update(id, data) {
    return this.axios.put(`/v1/api/privileged/permissions/${id}/`, data);
  }

  partialUpdate(id, data) {
    return this.axios.patch(`/v1/api/privileged/permissions/${id}/`, data);
  }

  destroy(id) {
    return this.axios.delete(`/v1/api/privileged/permissions/${id}/`);
  }
}

class Privileges {
  constructor(axiosInstance) {
    this.axios = axiosInstance;
  }

  list(params = {}) {
    return this.axios.get("/v1/api/privileged/privileges/", { params });
  }

  create(data) {
    return this.axios.post("/v1/api/privileged/privileges/", data);
  }

  retrieve(id) {
    return this.axios.get(`/v1/api/privileged/privileges/${id}/`);
  }

  update(id, data) {
    return this.axios.put(`/v1/api/privileged/privileges/${id}/`, data);
  }

  partialUpdate(id, data) {
    return this.axios.patch(`/v1/api/privileged/privileges/${id}/`, data);
  }

  destroy(id) {
    return this.axios.delete(`/v1/api/privileged/privileges/${id}/`);
  }
}

class Roles {
  constructor(axiosInstance) {
    this.axios = axiosInstance;
  }

  list(params = {}) {
    return this.axios.get("/v1/api/privileged/roles/", { params });
  }

  create(data) {
    return this.axios.post("/v1/api/privileged/roles/", data);
  }

  retrieve(id) {
    return this.axios.get(`/v1/api/privileged/roles/${id}/`);
  }

  update(id, data) {
    return this.axios.put(`/v1/api/privileged/roles/${id}/`, data);
  }

  partialUpdate(id, data) {
    return this.axios.patch(`/v1/api/privileged/roles/${id}/`, data);
  }

  destroy(id) {
    return this.axios.delete(`/v1/api/privileged/roles/${id}/`);
  }

  createRoleWebhook(url, data) {
    return this.axios.post(`/v1/api/privileged/role_webhook/${url}/`, data);
  }
}

class Servers {
  constructor(axiosInstance) {
    this.axios = axiosInstance;
  }

  list(params = {}) {
    return this.axios.get("/v1/api/privileged/servers/", { params });
  }

  create(data) {
    return this.axios.post("/v1/api/privileged/servers/", data);
  }

  retrieve(id) {
    return this.axios.get(`/v1/api/privileged/servers/${id}/`);
  }

  update(id, data) {
    return this.axios.put(`/v1/api/privileged/servers/${id}/`, data);
  }

  partialUpdate(id, data) {
    return this.axios.patch(`/v1/api/privileged/servers/${id}/`, data);
  }

  destroy(id) {
    return this.axios.delete(`/v1/api/privileged/servers/${id}/`);
  }

  getServerConfig(url) {
    return this.axios.get(`/v1/api/privileged/server_config/${url}/`, {
      responseType: "text",
    });
  }
}

class ServerPrivileges {
  constructor(axiosInstance) {
    this.axios = axiosInstance;
  }

  list(params = {}) {
    return this.axios.get("/v1/api/privileged/servers_privileges/", { params });
  }

  create(data) {
    return this.axios.post("/v1/api/privileged/servers_privileges/", data);
  }

  retrieve(id) {
    return this.axios.get(`/v1/api/privileged/servers_privileges/${id}/`);
  }

  update(id, data) {
    return this.axios.put(`/v1/api/privileged/servers_privileges/${id}/`, data);
  }

  partialUpdate(id, data) {
    return this.axios.patch(`/v1/api/privileged/servers_privileges/${id}/`, data);
  }

  destroy(id) {
    return this.axios.delete(`/v1/api/privileged/servers_privileges/${id}/`);
  }
}

class WebhookLogs {
  constructor(axiosInstance) {
    this.axios = axiosInstance;
  }

  list(params = {}) {
    return this.axios.get("/v1/api/privileged/webhook/", { params });
  }

  retrieve(id) {
    return this.axios.get(`/v1/api/privileged/webhook/${id}/`);
  }
}

class Rotations {
  constructor(axiosInstance) {
    this.axios = axiosInstance;
  }

  getCurrent(url) {
    return this.axios.get(`/v1/api/rotations/${url}/current/`, {
      responseType: "text",
    });
  }

  getNext(url) {
    return this.axios.get(`/v1/api/rotations/${url}/next/`, {
      responseType: "text",
    });
  }
}
