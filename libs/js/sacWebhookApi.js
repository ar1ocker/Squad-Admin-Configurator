//@ts-check
import axios from "axios";
import { subtle } from "node:crypto";

export default class SACWebhookApi {
  constructor(
    endpoint,
    webhookName,
    secretKey,
    signatureHeader = "X-SIGNATURE",
    hmacHashType = "SHA-256"
  ) {
    this.endpoint = endpoint;
    this.webhookName = webhookName;
    this.signatureHeader = signatureHeader;
    this.hmacHashType = hmacHashType;

    this.client = axios.create({ baseURL: this.endpoint });

    this._secret_key = secretKey;
    this._importedKey = null;

    this._encoder = new TextEncoder();
  }

  async _importKey() {
    this._importedKey = await subtle.importKey(
      "raw",
      this._encoder.encode(this._secret_key),
      { name: "HMAC", hash: this.hmacHashType },
      false,
      ["sign"]
    );

    this._secret_key = "";
  }

  async _computeSignatureForData(data) {
    if (this._importedKey === null) {
      await this._importKey();
    }

    //@ts-expect-error _importedKey is defined
    return Buffer.from(await subtle.sign("HMAC", this._importedKey, this._encoder.encode(data))).toString("hex");
  }

  async _getHeaders(path, data) {
    let signature = await this._computeSignatureForData(data);

    return {
      [this.signatureHeader]: signature,
      "Content-Type": "application/json",
    };
  }

  async callWebhook({steamID, name, durationUntilEnd, comment}) {
    let path = `/v1/api/privileged/role_webhook/${this.webhookName}/`;

    let data = JSON.stringify({ steam_id: steamID, name: name, duration_until_end: durationUntilEnd, comment: comment });

    let response = await this.client.post(path, data, {
      headers: await this._getHeaders(path, data),
    });

    return response;
  }
}