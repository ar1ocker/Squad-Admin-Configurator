//@ts-check
import BasePlugin from "./base-plugin.js";
import SACApi from "./sacApi.js";

export default class ShowMyRoles extends BasePlugin {
  static get description() {
    return "The plugin for showing user`s roles";
  }

  static get defaultEnabled() {
    return true;
  }

  static get optionsSpecification() {
    return {
      commands: {
        required: true,
        example: ["вип", "мойвип", "vip"],
      },

      api_endpoint: {
        required: true,
      },
      token: {
        required: true,
      },
    };
  }

  constructor(server, options, connectors) {
    super(server, options, connectors);
    this.sacAPI = new SACApi(this.options.api_endpoint, this.options.token);

    this.rolesMap = new Map(); // {id: title}

    this.updateRolesMap = this.updateRolesMap.bind(this);
  }

  async mount() {
    await this.updateRolesMap();

    this.server.on("ROUND_ENDED", this.updateRolesMap);

    for (const command of this.options.commands) {
      this.server.on(`CHAT_COMMAND:${command}`, (data) => {
        if (data.player) {
          this.messageProcessing(data.player);
        }
      });
    }
  }

  async messageProcessing(player) {
    let response;

    try {
      response = await this.sacAPI.serverPrivileges.list({
        privileged_steam_id: player.steamID,
        limit: 30,
        is_active: true,
      });
    } catch (error) {
      this.verbose(1, `Ошибка при получении списка привилегий ${error}`);
      await this.warn(player.steamID, "Ошибка при получении списка вип");
      return;
    }

    if (!response.data.count) {
      await this.warn(player.steamID, "Пока что у вас нет работающих привилегий :)");
      return;
    }

    let bulkMessages = [];

    for (let privileged of response.data.results) {
      let roleNames = [];
      for (let role of privileged.roles) {
        roleNames.push(this.rolesMap.get(role));
      }

      let formattedDate;
      if (privileged.date_of_end) {
        formattedDate = this.formatDate(new Date(privileged.date_of_end));
      } else {
        formattedDate = "бессрочно";
      }

      bulkMessages.push(`${formattedDate} - ${roleNames.join(", ")}`);

      if (bulkMessages.length > 3) {
        await this.warn(player.steamID, bulkMessages.join("\n"));
        bulkMessages = [];
        await new Promise((resolve) => setTimeout(resolve, 2 * 1000));
      }
    }

    if (bulkMessages.length) {
      await this.warn(player.steamID, bulkMessages.join("\n"));
    }
  }

  async updateRolesMap() {
    let response;
    try {
      response = await this.sacAPI.roles.list({ limit: 100 });
    } catch (error) {
      this.verbose(1, `Ошибка при получении списка ролей ${error}`);
      return;
    }

    for (let role of response.data.results) {
      this.rolesMap.set(role.id, role.title);
    }
  }

  formatDate(dt) {
    const day = dt.getDate().toString().padStart(2, "0");
    const month = (dt.getMonth() + 1).toString().padStart(2, "0");
    const hours = dt.getHours().toString().padStart(2, "0");
    const minutes = dt.getMinutes().toString().padStart(2, "0");
    const timezoneOffset = -dt.getTimezoneOffset() / 60;

    return `${day}-${month}-${dt.getFullYear()} ${hours}:${minutes} (UTC+${timezoneOffset})`;
  }

  async warn(playerID, message, repeat = 1, frequency = 5) {
    for (let i = 0; i < repeat; i++) {
      await this.server.rcon.warn(playerID, message + "\u{00A0}".repeat(i));

      if (i !== repeat - 1) {
        await new Promise((resolve) => setTimeout(resolve, frequency * 1000));
      }
    }
  }
}
