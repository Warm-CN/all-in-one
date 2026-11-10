import axios from "axios";

// This client deliberately has no global login interceptors: printer team sessions
// must never clear the club login or redirect a public visitor to /login.
export function printerApiBase(envUrl) {
  const base = String(envUrl ?? "/api").replace(/\/+$/, "");
  if (base.endsWith("/api/v1")) return `${base}/printers`;
  if (base.endsWith("/api")) return `${base}/v1/printers`;
  return `${base}/api/v1/printers`;
}

const client = axios.create({
  baseURL: printerApiBase(import.meta.env.VITE_API_BASE_URL),
  timeout: 15000,
});
export const printerSessionKey = "printer-booking-event-session-v2";
const auth = (token) => ({ headers: { Authorization: `Bearer ${token}` } });
async function call(method, path, data, token, params) {
  try {
    const res = await client.request({
      method,
      url: path,
      data,
      params,
      ...(token ? auth(token) : {}),
    });
    const body = res.data;
    if (body.code !== undefined && body.code !== 200)
      throw new Error(body.msg || "请求失败");
    return body.code !== undefined ? body.data : body;
  } catch (error) {
    const body = error.response?.data;
    const detail = body?.detail;
    const message =
      body?.msg ||
      (typeof detail === "string" ? detail : detail?.[0]?.msg) ||
      error.message ||
      "连接失败，请重试";
    const normalized = new Error(message);
    normalized.status = error.response?.status;
    throw normalized;
  }
}
export const printerApi = {
  config: () => call("get", "/config"),
  identify: (data) => call("post", "/identify", data),
  adminBookings: (date) =>
    call("get", "/admin/bookings", undefined, localStorage.getItem("token"), {
      date,
    }),
  addAdminBooking: (data) =>
    call("post", "/admin/bookings", data, localStorage.getItem("token")),
  deleteAdminBooking: (id) =>
    call(
      "delete",
      `/admin/bookings/${id}`,
      undefined,
      localStorage.getItem("token"),
    ),
  bookings: (date) => call("get", "/bookings", undefined, undefined, { date }),
  mine: (token) => call("get", "/my-bookings", undefined, token),
  reserve: (data, token) => call("post", "/bookings", data, token),
  action: (id, action, token) =>
    call("post", `/bookings/${id}/${action}`, {}, token),
  incident: (id, description, token) =>
    call("post", `/bookings/${id}/incidents`, { description }, token),
  adminConfig: () =>
    call("get", "/admin/config", undefined, localStorage.getItem("token")),
  saveConfig: (data) =>
    call("put", "/admin/config", data, localStorage.getItem("token")),
  setStatus: (id, status) =>
    call(
      "put",
      `/admin/printers/${id}`,
      { status },
      localStorage.getItem("token"),
    ),
  incidents: () =>
    call("get", "/admin/incidents", undefined, localStorage.getItem("token")),
  resolve: (id, resolution) =>
    call(
      "post",
      `/admin/incidents/${id}/resolve`,
      { resolution },
      localStorage.getItem("token"),
    ),
};
