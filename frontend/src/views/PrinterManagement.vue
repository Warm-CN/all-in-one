<template>
  <div class="printer-admin">
    <div class="admin-heading">
      <div>
        <h1>打印机管理</h1>
        <p>管理拓竹杯设备、办公室开放时间与异常交接记录。</p>
      </div>
      <router-link to="/printer-booking"
        ><el-button type="primary" plain>打开预约页面</el-button></router-link
      >
    </div>
    <el-alert
      v-if="error"
      :title="error"
      type="error"
      :closable="false"
      show-icon
      class="mb-5"
      ><template #default
        ><el-button text @click="load">重试</el-button></template
      ></el-alert
    >
    <div v-if="loading" class="loading-state" role="status">
      正在加载管理信息…
    </div>
    <template v-else-if="config">
      <section class="admin-card">
        <h2>设备状态</h2>
        <div class="devices">
          <article v-for="printer in config.printers" :key="printer.id">
            <div>
              <h3>{{ printer.name }}</h3>
              <el-tag
                :type="printer.status === 'available' ? 'success' : 'warning'"
                >{{
                  printer.status === "available" ? "开放预约" : "维护中"
                }}</el-tag
              >
            </div>
            <el-button
              :type="printer.status === 'available' ? 'warning' : 'success'"
              :loading="busy === `printer-${printer.id}`"
              @click="changeStatus(printer)"
              >{{
                printer.status === "available"
                  ? "暂停设备预约"
                  : "检查完成，恢复设备"
              }}</el-button
            >
          </article>
        </div>
        <p class="hint">
          维护状态会阻止新增预约。恢复前请确认设备安全，并检查已有预约安排。
        </p>
      </section>
      <section class="admin-card">
        <h2>绑定赛事与预约设置</h2>
        <p class="hint fixed-start-rule">
          每日可选的开始时段为 {{ openingText }}（北京时间，右端时刻不含）。单次预约最长 4 小时，结束时间可跨时段或跨天。
        </p>
        <el-form label-position="top" @submit.prevent="save">
          <div class="config-grid">
            <el-form-item label="绑定拓竹杯赛事">
              <el-select
                v-model="settings.module_key"
                placeholder="选择现有赛事"
                filterable
              >
                <el-option
                  v-for="event in config.events || []"
                  :key="event.id"
                  :label="event.name"
                  :value="event.module_key"
                />
              </el-select>
            </el-form-item>
            <el-form-item label="管理员联系方式（在设备日程公开显示）">
              <el-input
                v-model="settings.admin_contact"
                type="textarea"
                :rows="3"
                maxlength="300"
                show-word-limit
                placeholder="填写管理员姓名、手机号或微信等联系方式"
              />
            </el-form-item>
          </div>
          <el-button
            type="primary"
            native-type="submit"
            :loading="busy === 'config'"
            >保存设置</el-button
          ></el-form
        >
      </section>
      <section class="admin-card">
        <div class="incident-heading">
          <h2>当日预约管理</h2>
          <el-date-picker
            v-model="bookingDate"
            type="date"
            value-format="YYYY-MM-DD"
            :clearable="false"
            aria-label="管理预约日期"
            @change="loadBookings"
          />
        </div>
        <p class="hint">
          管理员可以直接添加或删除预约，无需审批。预约到点自动开始、到期自动结束，无需二次确认。同队可以同时预约不同设备；同机时间不能交叠。删除后释放时段，历史记录保留。
        </p>
        <el-form
          class="add-booking-form"
          label-position="top"
          @submit.prevent="addBooking"
        >
          <div class="config-grid">
            <el-form-item label="队长学号"
              ><el-input
                v-model="newBooking.captain_student_id"
                placeholder="已报名队伍的队长学号"
                maxlength="30"
            /></el-form-item>
            <el-form-item label="打印机"
              ><el-select v-model="newBooking.printer_id" placeholder="选择设备" @change="fillDefaultTimes"
                ><el-option
                  v-for="printer in config.printers"
                  :key="printer.id"
                  :label="printer.name"
                  :value="printer.id"
                  :disabled="printer.status !== 'available'" /></el-select
            ></el-form-item>
            <el-form-item label="开始时间（北京时间）"
              ><el-date-picker
                v-model="newBooking.start_time"
                type="datetime"
                value-format="YYYY-MM-DDTHH:mm:ss"
                format="YYYY-MM-DD HH:mm"
                placeholder="选择开始时间"
            /></el-form-item>
            <el-form-item label="结束时间"
              ><el-date-picker
                v-model="newBooking.end_time"
                type="datetime"
                value-format="YYYY-MM-DDTHH:mm:ss"
                format="YYYY-MM-DD HH:mm"
                placeholder="选择结束时间"
            /></el-form-item>
            <el-form-item label="打印用途"
              ><el-input
                v-model="newBooking.purpose"
                placeholder="填写用途"
                maxlength="500"
            /></el-form-item>
          </div>
          <el-button
            type="primary"
            native-type="submit"
            :loading="busy === 'add-booking'"
            >直接添加预约</el-button
          >
        </el-form>
        <div v-if="bookingsLoading" class="loading-state">正在加载预约…</div>
        <el-alert
          v-else-if="bookingsError"
          :title="bookingsError"
          type="error"
          :closable="false"
          ><template #default
            ><el-button text @click="loadBookings">重试</el-button></template
          ></el-alert
        >
        <el-empty v-else-if="!bookings.length" description="当日暂无预约" />
        <div v-else class="admin-bookings">
          <article v-for="booking in bookings" :key="booking.id">
            <div class="incident-heading">
              <h3>
                {{ printerName(booking.printer_id) }} · {{ booking.team_name }}
              </h3>
              <el-tag
                :type="
                  reservationStatus(booking, currentTime) === 'in_use'
                    ? 'warning'
                    : reservationStatus(booking, currentTime) === 'cancelled'
                      ? 'info'
                      : 'primary'
                "
                >{{ bookingStatus(booking) }}</el-tag
              >
            </div>
            <p>
              {{ formatTime(booking.start_time) }} →
              {{ formatTime(booking.end_time) }}
            </p>
            <p class="hint">
              队长：{{ booking.captain_name || "—" }} · 学号：{{
                booking.captain_student_id || "—"
              }}<template v-if="booking.purpose">
                · 用途：{{ booking.purpose }}</template
              >
            </p>
            <el-button
              v-if="booking.status !== 'cancelled'"
              type="danger"
              plain
              :loading="busy === `delete-${booking.id}`"
              @click="deleteBooking(booking)"
              >删除预约</el-button
            >
          </article>
        </div>
      </section>
      <section class="admin-card">
        <div class="incident-heading">
          <h2>设备异常记录</h2>
          <el-button :loading="incidentLoading" @click="loadIncidents"
            >刷新记录</el-button
          >
        </div>
        <p class="hint">
          异常关联上一预约占用记录。请结合现场情况核查责任，处理记录会保留；设备恢复需在上方单独操作。
        </p>
        <div v-if="incidentLoading" class="loading-state">
          正在加载异常记录…
        </div>
        <el-empty
          v-else-if="!incidents.length"
          description="暂无设备异常报告"
        />
        <div v-else class="incidents">
          <article v-for="incident in incidents" :key="incident.id">
            <div class="incident-heading">
              <h3>
                {{ printerName(incident.printer_id) }} · 异常 #{{ incident.id }}
              </h3>
              <el-tag :type="incident.resolved_at ? 'success' : 'warning'">{{
                incident.resolved_at ? "已处理" : "待核查"
              }}</el-tag>
            </div>
            <p class="description">{{ incident.description }}</p>
            <div class="incident-meta">
              <span
                >报告队伍：{{
                  incident.reporter_team_name || incident.team_name || "—"
                }}</span
              ><span>报告时间：{{ formatTime(incident.created_at) }}</span
              ><span
                >上一预约占用队伍：<strong>{{
                  incident.responsible_team_name || "暂无上一使用记录"
                }}</strong></span
              ><span
                >关联预约：{{
                  incident.previous_booking_id
                    ? `#${incident.previous_booking_id}`
                    : "无"
                }}</span
              >
            </div>
            <p v-if="incident.resolution" class="resolution">
              处理说明：{{ incident.resolution }}
            </p>
            <el-button
              v-if="!incident.resolved_at"
              type="primary"
              plain
              :loading="busy === `incident-${incident.id}`"
              @click="resolve(incident)"
              >记录核查结果</el-button
            >
          </article>
        </div>
      </section>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, onBeforeUnmount, reactive, ref } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { printerApi } from "@/api/printers";
import { reservationStatus, reservationLabel } from "@/utils/printerStatus";
const currentTime = ref(Date.now());
let statusClock;
const loading = ref(true),
  incidentLoading = ref(false),
  error = ref(""),
  config = ref(null),
  incidents = ref([]),
  busy = ref("");
const fixedStartWindows = [
  { start: "09:00", end: "12:00" },
  { start: "14:00", end: "17:00" },
  { start: "19:00", end: "21:30" },
];
const startWindows = computed(() =>
  config.value?.start_windows?.length ? config.value.start_windows : fixedStartWindows,
);
const openingText = computed(() =>
  startWindows.value.map(({ start, end }) => `${start}–${end}`).join("、"),
);
const settings = reactive({
  module_key: "bambu_cup",
  admin_contact: "",
});
const bookingDate = ref(
  new Intl.DateTimeFormat("sv-SE", {
    timeZone: "Asia/Shanghai",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).format(new Date()),
);
const bookings = ref([]),
  bookingsLoading = ref(false),
  bookingsError = ref("");
const newBooking = reactive({
  captain_student_id: "",
  printer_id: null,
  start_time: "",
  end_time: "",
  purpose: "",
});
function fillDefaultTimes() {
  if (newBooking.start_time || newBooking.end_time) return;

  const minute = 60_000;
  const day = 24 * 60 * minute;
  const beijingInput = (time) =>
    new Date(time + 8 * 60 * minute).toISOString().slice(0, 19);
  const nextMinute = (Math.floor(Date.now() / minute) + 1) * minute;
  const today = beijingInput(nextMinute).slice(0, 10);
  const date = bookingDate.value > today ? bookingDate.value : today;
  const midnight = Date.parse(`${date}T00:00:00+08:00`);

  for (const offset of [0, day]) {
    const windowDate = beijingInput(midnight + offset).slice(0, 10);
    for (const { start, end } of startWindows.value) {
      const candidate = Math.max(nextMinute, Date.parse(`${windowDate}T${start}:00+08:00`));
      if (candidate >= Date.parse(`${windowDate}T${end}:00+08:00`)) continue;
      newBooking.start_time = beijingInput(candidate);
      newBooking.end_time = beijingInput(candidate + 2 * 60 * minute);
      return;
    }
  }
}
let bookingsRequest = 0;
async function loadBookings() {
  const request = ++bookingsRequest;
  bookingsLoading.value = true;
  bookingsError.value = "";
  try {
    const data = await printerApi.adminBookings(bookingDate.value);
    if (request === bookingsRequest)
      bookings.value = Array.isArray(data) ? data : [];
  } catch (e) {
    if (request === bookingsRequest) {
      bookingsError.value = e.message;
      bookings.value = [];
    }
  } finally {
    if (request === bookingsRequest) bookingsLoading.value = false;
  }
}
async function addBooking() {
  if (
    !newBooking.captain_student_id.trim() ||
    !newBooking.printer_id ||
    !newBooking.start_time ||
    !newBooking.end_time ||
    !newBooking.purpose.trim()
  )
    return ElMessage.warning("请填写队长学号、设备、起止时间与用途");
  if (newBooking.start_time >= newBooking.end_time)
    return ElMessage.warning("结束时间必须晚于开始时间");
  // 管理员新增也遵守四小时限制，避免与队伍预约规则不一致。
  if (Date.parse(`${newBooking.end_time}+08:00`) - Date.parse(`${newBooking.start_time}+08:00`) > 4 * 3600000)
    return ElMessage.warning("单次预约时长不能超过 4 小时");
  if (Date.parse(`${newBooking.start_time}+08:00`) <= Date.now())
    return ElMessage.warning("开始时间必须晚于当前时间");
  const startTime = newBooking.start_time.slice(11, 16);
  if (!startWindows.value.some(({ start, end }) => start <= startTime && startTime < end)) {
    return ElMessage.warning(`开始时间须在每日开放时段内（${openingText.value}）`);
  }
  busy.value = "add-booking";
  try {
    await printerApi.addAdminBooking({
      ...newBooking,
      captain_student_id: newBooking.captain_student_id.trim(),
      start_time: `${newBooking.start_time}+08:00`,
      end_time: `${newBooking.end_time}+08:00`,
    });
    bookingDate.value = newBooking.start_time.slice(0, 10);
    ElMessage.success("预约已添加");
    await loadBookings();
  } catch (e) {
    ElMessage.error(e.message);
  } finally {
    busy.value = "";
  }
}
async function deleteBooking(booking) {
  try {
    await ElMessageBox.confirm(
      `确认删除 ${booking.team_name} 在 ${printerName(booking.printer_id)} 的预约？删除后释放时段，使用与异常历史仍保留。`,
      "删除预约",
      {
        type: "warning",
        confirmButtonText: "确认删除",
        cancelButtonText: "返回",
      },
    );
  } catch {
    return;
  }
  busy.value = `delete-${booking.id}`;
  try {
    await printerApi.deleteAdminBooking(booking.id);
    ElMessage.success("预约已删除，历史已保留");
    await loadBookings();
  } catch (e) {
    ElMessage.error(e.message);
  } finally {
    busy.value = "";
  }
}
const bookingStatus = (b) =>
  reservationStatus(b, currentTime.value) === "cancelled" && b.deleted_by
    ? "管理员已删除"
    : reservationLabel(b, currentTime.value);
async function load() {
  loading.value = true;
  error.value = "";
  try {
    config.value = await printerApi.adminConfig();
    Object.assign(settings, {
      module_key: config.value.module_key,
      admin_contact: config.value.admin_contact || "",
    });
    await Promise.all([loadIncidents(), loadBookings()]);
  } catch (e) {
    error.value = e.message;
  } finally {
    loading.value = false;
  }
}
async function loadIncidents() {
  incidentLoading.value = true;
  try {
    const data = await printerApi.incidents();
    incidents.value = Array.isArray(data) ? data : data.incidents || [];
  } catch (e) {
    error.value = e.message;
  } finally {
    incidentLoading.value = false;
  }
}
async function changeStatus(p) {
  const next = p.status === "available" ? "maintenance" : "available";
  try {
    await ElMessageBox.confirm(
      next === "maintenance"
        ? "暂停后该设备无法新增预约，已有预约仍会保留。确认暂停？"
        : "确认已检查设备，可以恢复预约和使用？",
      "设备状态",
      { confirmButtonText: "确认", cancelButtonText: "返回", type: "warning" },
    );
  } catch {
    return;
  }
  busy.value = `printer-${p.id}`;
  try {
    await printerApi.setStatus(p.id, next);
    p.status = next;
    ElMessage.success("设备状态已更新");
  } catch (e) {
    ElMessage.error(e.message);
  } finally {
    busy.value = "";
  }
}
async function save() {
  if (!settings.module_key?.trim()) return ElMessage.warning("请选择绑定赛事");
  busy.value = "config";
  try {
    await printerApi.saveConfig({ ...settings });
    config.value = await printerApi.adminConfig();
    ElMessage.success("设置已保存");
  } catch (e) {
    ElMessage.error(e.message);
  } finally {
    busy.value = "";
  }
}
async function resolve(incident) {
  let result;
  try {
    result = await ElMessageBox.prompt(
      "请填写现场核查、责任确认及维修处理结果。",
      "记录异常处理",
      {
        inputType: "textarea",
        inputValidator: (value) =>
          value?.trim().length >= 5 || "请填写至少5个字",
        confirmButtonText: "保存处理结果",
        cancelButtonText: "返回",
      },
    );
  } catch {
    return;
  }
  busy.value = `incident-${incident.id}`;
  try {
    await printerApi.resolve(incident.id, result.value.trim());
    ElMessage.success("处理记录已保存");
    await loadIncidents();
  } catch (e) {
    ElMessage.error(e.message);
  } finally {
    busy.value = "";
  }
}
const printerName = (id) =>
  // 历史预约和异常仍可显示下架设备名称，不重新开放该设备。
  config.value?.printers.find((p) => p.id === id)?.name ||
  (config.value?.retired_printer_names?.[id] ? `${config.value.retired_printer_names[id]}（已下架）` : `打印机 ${id}`);
const formatTime = (value) =>
  value ? String(value).replace("T", " ").slice(0, 16) : "—";
onMounted(() => {
  load();
  statusClock = window.setInterval(() => {
    currentTime.value = Date.now();
  }, 1000);
});
onBeforeUnmount(() => window.clearInterval(statusClock));
</script>

<style scoped>
.add-booking-form {
  margin-top: 20px;
}
.admin-bookings {
  display: grid;
  gap: 14px;
  margin-top: 22px;
}
.admin-bookings article {
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  padding: 18px;
  background: white;
}
.admin-bookings article > .el-button {
  margin-top: 12px;
}
.config-grid :deep(.el-select),
.config-grid :deep(.el-date-editor) {
  width: 100%;
}

.printer-admin {
  max-width: 1180px;
  margin: auto;
  color: #0f172a;
}
.admin-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 24px;
}
.admin-heading h1 {
  font-size: 28px;
  font-weight: 800;
}
.admin-heading p,
.hint {
  margin-top: 8px;
  color: #64748b;
  font-size: 13px;
  line-height: 1.8;
}
.admin-card {
  margin-top: 20px;
  border: 1px solid #e2e8f0;
  border-radius: 22px;
  background: linear-gradient(135deg, #fff, #f8fafc);
  padding: 24px;
}
.admin-card h2 {
  font-size: 19px;
  font-weight: 800;
  margin-bottom: 18px;
}
.devices {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 14px;
}
.devices article {
  padding: 18px;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  background: #fff;
}
.devices article > div {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
}
.devices h3 {
  font-size: 16px;
  font-weight: 700;
}
.devices .el-button {
  width: 100%;
}
.fixed-start-rule {
  margin-bottom: 16px;
}
.config-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-top: 20px;
}
.incident-heading {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 14px;
}
.incident-heading h2 {
  margin-bottom: 0;
}
.incident-heading h3 {
  font-size: 15px;
  font-weight: 700;
}
.incidents {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-top: 22px;
}
.incidents article {
  padding: 18px;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  background: white;
}
.description {
  margin: 14px 0;
  font-size: 14px;
  line-height: 1.8;
  white-space: pre-wrap;
  overflow-wrap: anywhere;
}
.incident-meta {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  font-size: 12px;
  color: #64748b;
  margin-bottom: 16px;
}
.resolution {
  padding: 12px;
  background: #f0fdf4;
  border-radius: 10px;
  color: #166534;
  font-size: 13px;
  line-height: 1.8;
  white-space: pre-wrap;
}
.loading-state {
  padding: 50px 10px;
  color: #64748b;
  text-align: center;
}
:deep(.el-button) {
  border-radius: 10px;
}
:deep(.el-input__wrapper) {
  border-radius: 10px;
}
@media (max-width: 900px) {
  .devices {
    grid-template-columns: 1fr;
  }
}
@media (max-width: 600px) {
  .admin-heading {
    align-items: flex-start;
    flex-direction: column;
  }
  .admin-card {
    padding: 18px 14px;
  }
  .config-grid,
  .incident-meta {
    grid-template-columns: 1fr;
  }
  .incident-heading {
    flex-wrap: wrap;
  }
  .admin-heading h1 {
    font-size: 24px;
  }
}
</style>
