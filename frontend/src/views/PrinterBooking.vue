<template>
  <main class="printer-page">
    <div class="printer-shell">
      <header class="portal-hero">
        <div>
          <div class="badges">
            <span>拓竹杯</span><span class="mint">共享设备 · 有序使用</span>
          </div>
          <div class="hero-title">
            <img src="@/assets/images/logo.png" alt="无线电爱好者协会" />
            <h1>打印机预约中心</h1>
          </div>
          <p>
            选一台打印机，约好你的创作时间。使用前签到，完成后归还，让下一支队伍安心接力。
          </p>
        </div>
        <aside class="hero-summary">
          <span class="eyebrow">预约规则</span
          ><strong>3 台设备，各自独立预约</strong>
          <p>
            无需审批，同队可同时预约三台设备。时间以北京时间为准，开始时间遵循已启用的开放规则。
          </p>
        </aside>
      </header>

      <el-alert
        v-if="error"
        :title="error"
        type="error"
        show-icon
        :closable="false"
        ><template #default
          ><el-button text type="primary" @click="loadAll"
            >重新加载</el-button
          ></template
        ></el-alert
      >
      <section class="glass-card">
        <div class="surface-header">
          <nav class="segments" aria-label="预约中心导航">
            <button
              v-for="item in tabs"
              :key="item.key"
              :class="{ active: tab === item.key }"
              @click="tab = item.key"
            >
              {{ item.label }}
            </button>
          </nav>
        </div>
        <div class="panel-body">
          <div v-if="loading" class="state-panel" role="status">
            <el-icon class="is-loading" :size="28"><Loading /></el-icon>
            <p>正在加载设备与日程…</p>
          </div>
          <template v-else>
            <section v-if="tab === 'schedule'">
              <div class="section-heading">
                <div>
                  <h2>设备日程</h2>
                  <p>同一台设备的预约不可重叠；相邻时间可以接续预约。</p>
                </div>
                <el-date-picker
                  v-model="selectedDate"
                  type="date"
                  value-format="YYYY-MM-DD"
                  :clearable="false"
                  aria-label="查看日程日期"
                  @change="loadSchedule"
                />
              </div>
              <div v-if="scheduleLoading" class="state-panel" role="status">
                正在更新日程…
              </div>
              <div v-else class="machine-grid">
                <article
                  v-for="printer in config.printers"
                  :key="printer.id"
                  class="machine-card"
                >
                  <div class="machine-head">
                    <div class="device-icon">
                      <el-icon :size="25"><Printer /></el-icon>
                    </div>
                    <el-tag
                      :type="
                        printer.status === 'available' ? 'success' : 'warning'
                      "
                      effect="light"
                      >{{
                        printer.status === "available" ? "开放预约" : "维护中"
                      }}</el-tag
                    >
                  </div>
                  <h3>{{ printer.name }}</h3>
                  <p class="muted">
                    {{ printer.description || "拓竹杯共享打印设备" }}
                  </p>
                  <div class="day-track" aria-hidden="true">
                    <i
                      v-for="booking in printerBookings(printer.id)"
                      :key="booking.id"
                      :style="barStyle(booking)"
                    />
                  </div>
                  <div class="track-labels">
                    <span>00:00</span><span>12:00</span><span>24:00</span>
                  </div>
                  <div
                    v-if="!printerBookings(printer.id).length"
                    class="empty-slots"
                  >
                    当天暂无预约
                  </div>
                  <ul v-else class="slot-list">
                    <li
                      v-for="booking in printerBookings(printer.id)"
                      :key="booking.id"
                    >
                      <span>{{ timeRange(booking) }}</span
                      ><strong>{{ booking.team_name }}</strong
                      ><el-tag
                        size="small"
                        :type="
                          statusType(reservationStatus(booking, currentTime))
                        "
                        >{{ reservationLabel(booking, currentTime) }}</el-tag
                      >
                    </li>
                  </ul>
                  <el-button
                    class="reserve-button"
                    type="primary"
                    plain
                    :disabled="printer.status !== 'available'"
                    @click="choosePrinter(printer.id)"
                    >预约这台设备</el-button
                  >
                </article>
              </div>
              <div class="rule-note">
                <el-icon><InfoFilled /></el-icon>
                <div>
                  <strong>办公室开放时间</strong>
                  <p v-if="!config.opening_hours_enabled">
                    当前未限制预约开始时间。请确认现场开放后再到场使用。
                  </p>
                  <p v-else>
                    {{ openingText || "尚未配置可预约时段，请联系管理员。" }}
                  </p>
                  <p>
                    检查设备后再签到；发现异常请在对应预约中报告，系统会记录上一实际使用队伍，由管理员核实处理。
                  </p>
                </div>
              </div>
            </section>

            <section v-if="tab === 'reserve'">
              <div class="section-heading">
                <div>
                  <h2>预约打印时间</h2>
                  <p>
                    先输入队长学号查询队伍，再选择设备与开始、结束时间。同队可以同时预约不同设备。
                  </p>
                </div>
              </div>
              <div v-if="!session" class="state-panel">
                <p>请先输入队长学号查询参赛队伍</p>
                <el-button type="primary" @click="tab = 'identity'"
                  >去查询队伍</el-button
                >
              </div>
              <template v-else
                ><div class="identity-strip">
                  <span
                    >当前队伍：<strong>{{
                      session.team.team_name
                    }}</strong></span
                  ><el-button text @click="tab = 'identity'"
                    >切换队伍</el-button
                  >
                </div>
                <el-form
                  label-position="top"
                  size="large"
                  @submit.prevent="reserve"
                >
                  <div class="form-grid">
                    <el-form-item label="打印机"
                      ><el-select
                        v-model="form.printer_id"
                        placeholder="选择设备"
                        ><el-option
                          v-for="p in config.printers"
                          :key="p.id"
                          :label="
                            p.name +
                            (p.status === 'maintenance' ? '（维护中）' : '')
                          "
                          :value="p.id"
                          :disabled="
                            p.status !== 'available'
                          " /></el-select></el-form-item
                    ><el-form-item label="打印用途"
                      ><el-input
                        v-model="form.purpose"
                        maxlength="500"
                        placeholder="如：底盘支架、外壳原型" /></el-form-item
                    ><el-form-item label="开始时间（北京时间）"
                      ><el-date-picker
                        v-model="form.start_time"
                        type="datetime"
                        value-format="YYYY-MM-DDTHH:mm:ss"
                        format="YYYY-MM-DD HH:mm"
                        :editable="false"
                        placeholder="选择开始时间" /></el-form-item
                    ><el-form-item label="结束时间（可跨天）"
                      ><el-date-picker
                        v-model="form.end_time"
                        type="datetime"
                        value-format="YYYY-MM-DDTHH:mm:ss"
                        format="YYYY-MM-DD HH:mm"
                        :editable="false"
                        placeholder="选择结束时间"
                    /></el-form-item>
                  </div>
                  <p class="muted form-tip">
                    提交后立即占用该时间段，请合理预估耗时。设备日程可能变化，最终以提交结果为准。
                  </p>
                  <el-button
                    type="primary"
                    :loading="submitting"
                    native-type="submit"
                    >确认预约</el-button
                  >
                </el-form>
              </template>
            </section>

            <section v-if="tab === 'mine'">
              <div class="section-heading">
                <div>
                  <h2>我的预约</h2>
                  <p>
                    使用前检查设备并签到，使用后及时归还。发现异常请保留现场并报告。
                  </p>
                </div>
                <el-button
                  v-if="session"
                  :loading="mineLoading"
                  @click="loadMine"
                  >刷新</el-button
                >
              </div>
              <div v-if="!session" class="state-panel">
                <p>查询到参赛队伍后查看预约记录</p>
                <el-button type="primary" @click="tab = 'identity'"
                  >去查询队伍</el-button
                >
              </div>
              <div v-else-if="mineLoading" class="state-panel" role="status">
                正在加载预约…
              </div>
              <el-empty
                v-else-if="!mine.length"
                description="你的队伍还没有预约"
                ><el-button type="primary" @click="tab = 'schedule'"
                  >看看可用设备</el-button
                ></el-empty
              >
              <div v-else class="booking-list">
                <article
                  v-for="booking in mine"
                  :key="booking.id"
                  class="booking-card"
                >
                  <div class="booking-heading">
                    <div>
                      <h3>{{ printerName(booking.printer_id) }}</h3>
                      <p>{{ fullRange(booking) }}</p>
                    </div>
                    <el-tag
                      :type="
                        statusType(reservationStatus(booking, currentTime))
                      "
                      >{{ reservationLabel(booking, currentTime) }}</el-tag
                    >
                  </div>
                  <p v-if="booking.purpose" class="muted">
                    {{ booking.purpose }}
                  </p>
                  <p class="handover">
                    上一实际使用队伍：<strong>{{
                      previousTeam(booking)
                    }}</strong>
                  </p>
                  <p v-if="booking.checked_in_at" class="muted">
                    签到：{{ fullTime(booking.checked_in_at)
                    }}<template v-if="booking.checked_out_at">
                      · 归还：{{ fullTime(booking.checked_out_at) }}</template
                    >
                  </p>
                  <div class="booking-actions">
                    <el-button
                      v-if="canCancel(booking)"
                      :loading="busyId === booking.id"
                      @click="bookingAction(booking, 'cancel')"
                      >取消预约</el-button
                    ><el-button
                      v-if="canCheckIn(booking)"
                      type="primary"
                      :loading="busyId === booking.id"
                      @click="bookingAction(booking, 'check-in')"
                      >检查完成，签到</el-button
                    ><el-button
                      v-if="usageStatus(booking) === 'in_use'"
                      type="success"
                      :loading="busyId === booking.id"
                      @click="bookingAction(booking, 'check-out')"
                      >完成使用并归还</el-button
                    ><el-button
                      v-if="canReport(booking)"
                      type="warning"
                      plain
                      @click="openIncident(booking)"
                      >报告设备异常</el-button
                    >
                  </div>
                </article>
              </div>
            </section>

            <section v-if="tab === 'identity'">
              <div class="section-heading">
                <div>
                  <h2>队伍身份</h2>
                  <p>直接查询已报名的拓竹杯队伍，无需登录社团账号。</p>
                </div>
              </div>
              <div v-if="session" class="identity-strip">
                <span
                  >已核验：<strong>{{ session.team.team_name }}</strong></span
                ><el-button @click="logout">退出队伍</el-button>
              </div>
              <template v-else>
                <p class="muted form-tip">
                  当前赛事：{{
                    config.event?.name || "尚未绑定拓竹杯赛事"
                  }}。输入报名时填写的队长学号，查到参赛队伍后即可预约。
                </p>
                <el-form
                  label-position="top"
                  size="large"
                  @submit.prevent="identify"
                >
                  <el-form-item label="队长学号">
                    <el-input
                      v-model="identity.captain_student_id"
                      autocomplete="username"
                      maxlength="30"
                      placeholder="请输入已报名队伍的队长学号"
                    />
                  </el-form-item>
                  <el-button
                    type="primary"
                    native-type="submit"
                    :loading="submitting"
                    :disabled="!config.event"
                    >查询队伍</el-button
                  >
                </el-form>
                <el-alert
                  v-if="identityError"
                  :title="identityError"
                  type="warning"
                  :closable="false"
                  show-icon
                  class="identity-error"
                />
                <div class="signup-link">
                  <p class="muted">
                    还没有参赛队伍？先完成对应赛事的组队报名，再返回查询。
                  </p>
                  <router-link :to="signupUrl"
                    ><el-button plain type="primary"
                      >前往{{ config.event?.name || "赛事" }}报名</el-button
                    ></router-link
                  >
                </div>
              </template>
            </section>
          </template>
        </div>
      </section>
      <footer class="portal-footer">
        <router-link :to="signupUrl">对应赛事报名</router-link><span>·</span
        ><router-link to="/apply">招新报名</router-link><span>·</span
        ><router-link to="/admin/printers">管理员入口</router-link>
      </footer>
    </div>
    <el-dialog
      v-model="incidentVisible"
      title="报告设备异常"
      width="min(560px, 94vw)"
      ><p class="incident-note">
        请描述发现时间、异常现象及现场情况。上一实际使用队伍：<strong>{{
          previousTeam(incidentBooking)
        }}</strong
        >。系统记录用于核查，不代表自动认定责任。
      </p>
      <el-input
        v-model="incidentDescription"
        type="textarea"
        :rows="5"
        maxlength="2000"
        show-word-limit
        placeholder="例如：签到前检查发现喷嘴堵塞，打印平台有明显残留…"
      /><template #footer
        ><el-button @click="incidentVisible = false">取消</el-button
        ><el-button type="warning" :loading="submitting" @click="submitIncident"
          >提交异常报告</el-button
        ></template
      ></el-dialog
    >
  </main>
</template>

<script setup>
import { computed, onMounted, onBeforeUnmount, reactive, ref } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { Loading, Printer, InfoFilled } from "@element-plus/icons-vue";
import { printerApi, printerSessionKey } from "@/api/printers";
import {
  reservationStatus,
  reservationLabel,
  usageStatus,
} from "@/utils/printerStatus";
const tabs = [
  { key: "schedule", label: "设备日程" },
  { key: "reserve", label: "预约时间" },
  { key: "mine", label: "我的预约" },
  { key: "identity", label: "队伍身份" },
];
const tab = ref("schedule"),
  config = ref({
    printers: [],
    opening_hours: [],
    opening_hours_enabled: false,
  }),
  bookings = ref([]),
  mine = ref([]);
const loading = ref(true),
  scheduleLoading = ref(false),
  mineLoading = ref(false),
  submitting = ref(false),
  busyId = ref(null),
  error = ref("");
function shanghaiDate() {
  return new Intl.DateTimeFormat("sv-SE", {
    timeZone: "Asia/Shanghai",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).format(new Date());
}
const selectedDate = ref(shanghaiDate()),
  session = ref(null);
try {
  sessionStorage.removeItem("printer-booking-session");
  const cached = JSON.parse(
    sessionStorage.getItem(printerSessionKey) || "null",
  );
  if (cached?.token && cached?.team?.id) session.value = cached;
  else sessionStorage.removeItem(printerSessionKey);
} catch {
  sessionStorage.removeItem(printerSessionKey);
}
const identity = reactive({ captain_student_id: "" });
const identityError = ref("");
const signupUrl = computed(
  () =>
    config.value.signup_url ||
    (config.value.event?.id
      ? `/team-portal?event_id=${config.value.event.id}`
      : "/team-portal"),
);
const form = reactive({
  printer_id: null,
  start_time: "",
  end_time: "",
  purpose: "",
});
const incidentVisible = ref(false),
  incidentBooking = ref(null),
  incidentDescription = ref("");
const weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"];
const openingText = computed(() =>
  (config.value.opening_hours || [])
    .map((h) => `${weekdays[h.weekday]} ${h.start}–${h.end}`)
    .join("；"),
);
const list = (data) => (Array.isArray(data) ? data : data?.bookings || []);
function fail(e) {
  ElMessage.error(e.message);
  if (e.status === 401 && session.value) {
    logout();
    tab.value = "identity";
  }
}
async function loadAll() {
  loading.value = true;
  error.value = "";
  try {
    config.value = await printerApi.config();
    await loadSchedule();
    if (session.value) await loadMine();
  } catch (e) {
    error.value = e.message;
  } finally {
    loading.value = false;
  }
}
let scheduleRequest = 0;
async function loadSchedule() {
  const request = ++scheduleRequest;
  scheduleLoading.value = true;
  try {
    const data = await printerApi.bookings(selectedDate.value);
    if (request === scheduleRequest) {
      bookings.value = list(data);
      error.value = "";
    }
  } catch (e) {
    if (request === scheduleRequest) {
      bookings.value = [];
      error.value = e.message;
    }
  } finally {
    if (request === scheduleRequest) scheduleLoading.value = false;
  }
}
async function loadMine() {
  if (!session.value) return;
  mineLoading.value = true;
  try {
    mine.value = list(await printerApi.mine(session.value.token));
  } catch (e) {
    fail(e);
  } finally {
    mineLoading.value = false;
  }
}
function logout() {
  session.value = null;
  mine.value = [];
  sessionStorage.removeItem(printerSessionKey);
}
async function identify() {
  if (!identity.captain_student_id.trim())
    return ElMessage.warning("请输入队长学号");
  submitting.value = true;
  identityError.value = "";
  try {
    const data = await printerApi.identify({
      captain_student_id: identity.captain_student_id.trim(),
    });
    session.value = { token: data.token, team: data.team };
    sessionStorage.setItem(printerSessionKey, JSON.stringify(session.value));
    mine.value = list(data.bookings);
    await loadMine();
    ElMessage.success("已查到参赛队伍");
    tab.value = form.printer_id ? "reserve" : "mine";
  } catch (e) {
    identityError.value = e.message;
  } finally {
    submitting.value = false;
  }
}
function choosePrinter(id) {
  form.printer_id = id;
  if (!form.start_time || form.start_time.slice(0, 10) !== selectedDate.value) {
    const desired = new Date(`${selectedDate.value}T09:00:00+08:00`).getTime();
    const start = Math.max(
      desired,
      Math.ceil((Date.now() + 60000) / 1800000) * 1800000,
    );
    const beijingInput = (time) =>
      new Date(time + 8 * 3600000).toISOString().slice(0, 19);
    form.start_time = beijingInput(start);
    form.end_time = beijingInput(start + 2 * 3600000);
  }
  tab.value = session.value ? "reserve" : "identity";
}
const currentTime = ref(Date.now());
let clock;
const instant = (value) =>
  new Date(
    /(Z|[+-]\d\d:\d\d)$/.test(value) ? value : `${value}+08:00`,
  ).getTime();
const duringBooking = (b) =>
  instant(b.start_time) <= currentTime.value &&
  currentTime.value < instant(b.end_time);
const canCancel = (b) =>
  usageStatus(b) === "reserved" && instant(b.start_time) > currentTime.value;
const canCheckIn = (b) =>
  usageStatus(b) === "reserved" &&
  duringBooking(b) &&
  config.value.printers.find((p) => p.id === b.printer_id)?.status ===
    "available";
const canReport = (b) =>
  usageStatus(b) === "in_use" ||
  (usageStatus(b) === "reserved" && duringBooking(b));
async function reserve() {
  if (!session.value) return;
  if (
    !form.printer_id ||
    !form.start_time ||
    !form.end_time ||
    !form.purpose.trim()
  )
    return ElMessage.warning("请选择设备、起止时间并填写打印用途");
  if (form.start_time >= form.end_time)
    return ElMessage.warning("结束时间必须晚于开始时间");
  if (new Date(`${form.start_time}+08:00`).getTime() <= Date.now())
    return ElMessage.warning("开始时间必须晚于当前时间");
  submitting.value = true;
  try {
    await printerApi.reserve(
      {
        ...form,
        start_time: `${form.start_time}+08:00`,
        end_time: `${form.end_time}+08:00`,
      },
      session.value.token,
    );
    ElMessage.success("预约成功");
    selectedDate.value = form.start_time.slice(0, 10);
    await Promise.all([loadMine(), loadSchedule()]);
    tab.value = "mine";
  } catch (e) {
    fail(e);
    if (e.status === 409) await loadSchedule();
  } finally {
    submitting.value = false;
  }
}
async function bookingAction(booking, action) {
  const messages = {
    cancel: "确认取消这次预约？取消后该时间段将释放。",
    "check-in": "确认已在现场检查设备，准备开始使用？",
    "check-out": "确认打印已完成、设备与现场已整理，可以交给下一队伍？",
  };
  try {
    await ElMessageBox.confirm(messages[action], "确认操作", {
      confirmButtonText: "确认",
      cancelButtonText: "返回",
      type: action === "cancel" ? "warning" : "info",
    });
  } catch {
    return;
  }
  busyId.value = booking.id;
  try {
    await printerApi.action(booking.id, action, session.value.token);
    ElMessage.success("操作成功");
    await Promise.all([loadMine(), loadSchedule()]);
  } catch (e) {
    fail(e);
  } finally {
    busyId.value = null;
  }
}
function openIncident(booking) {
  incidentBooking.value = booking;
  incidentDescription.value = "";
  incidentVisible.value = true;
}
async function submitIncident() {
  if (incidentDescription.value.trim().length < 5)
    return ElMessage.warning("请填写至少5个字的异常描述");
  submitting.value = true;
  try {
    const report = await printerApi.incident(
      incidentBooking.value.id,
      incidentDescription.value.trim(),
      session.value.token,
    );
    ElMessage.success(
      `异常已记录。上一实际使用队伍：${report.responsible_team_name || "无上一记录"}，等待管理员核查`,
    );
    incidentVisible.value = false;
    config.value = await printerApi.config();
    await Promise.all([loadMine(), loadSchedule()]);
  } catch (e) {
    fail(e);
  } finally {
    submitting.value = false;
  }
}
const printerBookings = (id) =>
  bookings.value
    .filter((b) => b.printer_id === id && b.status !== "cancelled")
    .sort((a, b) => a.start_time.localeCompare(b.start_time));
const printerName = (id) =>
  config.value.printers.find((p) => p.id === id)?.name || `打印机 ${id}`;
function fullTime(value) {
  if (!value) return "—";
  return String(value)
    .replace("T", " ")
    .replace(/([+-]\d\d:\d\d|Z)$/, "")
    .slice(0, 16);
}
function fullRange(b) {
  return `${fullTime(b.start_time)} → ${fullTime(b.end_time)}`;
}
function timeRange(b) {
  const start = fullTime(b.start_time),
    end = fullTime(b.end_time);
  return `${start.slice(0, 10) === selectedDate.value ? start.slice(11) : "前日"} – ${end.slice(0, 10) === selectedDate.value ? end.slice(11) : "次日"}`;
}
function barStyle(b) {
  const begin = new Date(`${selectedDate.value}T00:00:00+08:00`).getTime();
  const instant = (value) =>
    new Date(
      /(Z|[+-]\d\d:\d\d)$/.test(value) ? value : `${value}+08:00`,
    ).getTime();
  const left = Math.max(0, ((instant(b.start_time) - begin) / 86400000) * 100);
  const right = Math.min(100, ((instant(b.end_time) - begin) / 86400000) * 100);
  return { left: `${left}%`, width: `${Math.max(0, right - left)}%` };
}
function previousTeam(b) {
  if (b?.previous_team_name) return b.previous_team_name;
  if (b && usageStatus(b) === "reserved")
    return "将在签到或提交异常时根据实际使用记录确定";
  return "暂无上一使用记录";
}
function statusType(s) {
  return (
    {
      reserved: "primary",
      in_use: "warning",
      completed: "success",
      cancelled: "info",
    }[s] || "info"
  );
}
onMounted(() => {
  loadAll();
  clock = window.setInterval(() => {
    currentTime.value = Date.now();
  }, 1000);
});
onBeforeUnmount(() => window.clearInterval(clock));
</script>

<style scoped>
.signup-link {
  margin-top: 24px;
}
.signup-link .el-button {
  margin-top: 10px;
}
.identity-error {
  margin-top: 18px;
}
.printer-page {
  min-height: 100vh;
  padding: 32px 24px;
  background: linear-gradient(135deg, #eef7ff 0%, #f8fafc 48%, #ecfdf8 100%);
  color: #0f172a;
}
.printer-shell {
  max-width: 1180px;
  margin: auto;
  display: flex;
  flex-direction: column;
  gap: 24px;
}
.portal-hero {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 300px;
  gap: 28px;
  align-items: center;
  padding: 32px;
  border: 1px solid #ffffffb3;
  border-radius: 28px;
  background: linear-gradient(135deg, #fffffff5, #f0f9ffe6 58%, #ecfdf5db);
  box-shadow: 0 24px 58px -44px #0f172a73;
}
.badges {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 16px;
}
.badges span {
  padding: 5px 12px;
  border: 1px solid #bae6fd;
  border-radius: 30px;
  background: #f0f9ff;
  color: #0369a1;
  font-size: 12px;
  font-weight: 700;
}
.badges .mint {
  background: #ecfdf5;
  border-color: #a7f3d0;
  color: #047857;
}
.hero-title {
  display: flex;
  align-items: center;
  gap: 16px;
}
.hero-title img {
  width: 68px;
  height: 68px;
  object-fit: contain;
}
.hero-title h1 {
  font-size: 38px;
  font-weight: 900;
  line-height: 1.25;
  letter-spacing: -1px;
}
.portal-hero p {
  margin-top: 14px;
  font-size: 15px;
  line-height: 1.9;
  color: #64748b;
}
.hero-summary {
  border: 1px solid #e2e8f0;
  border-radius: 18px;
  padding: 18px;
  background: #ffffffcc;
}
.hero-summary strong {
  display: block;
  margin-top: 10px;
  font-size: 17px;
}
.hero-summary p {
  font-size: 13px;
  margin-top: 8px;
}
.eyebrow {
  font-size: 11px;
  font-weight: 700;
  color: #94a3b8;
}
.glass-card {
  border: 1px solid #ffffffb3;
  border-radius: 28px;
  overflow: hidden;
  background: linear-gradient(180deg, #fffffff5, #f8fafceb);
  box-shadow: 0 22px 66px -44px #0f172a73;
  backdrop-filter: blur(8px);
}
.surface-header {
  padding: 16px;
  background: #ffffffbf;
  border-bottom: 1px solid #e2e8f0;
}
.segments {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 4px;
  max-width: 760px;
  margin: auto;
  padding: 4px;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  background: #f8fafc;
}
.segments button {
  min-height: 48px;
  border: 0;
  border-radius: 12px;
  color: #64748b;
  background: transparent;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
}
.segments button.active {
  background: linear-gradient(145deg, #fff, #f0f9ff);
  color: #0369a1;
  box-shadow: 0 6px 14px #0284c726;
}
.segments button:focus-visible {
  outline: 2px solid #0284c7;
  outline-offset: 1px;
}
.panel-body {
  padding: 28px;
}
.section-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 24px;
}
.section-heading h2 {
  font-size: 22px;
  font-weight: 800;
}
.section-heading p {
  font-size: 14px;
  line-height: 1.7;
  color: #64748b;
  margin-top: 6px;
}
.machine-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 18px;
}
.machine-card {
  min-width: 0;
  display: flex;
  flex-direction: column;
  padding: 20px;
  border: 1px solid #e2e8f0;
  border-radius: 22px;
  background: #fff;
}
.machine-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 18px;
}
.device-icon {
  display: grid;
  place-items: center;
  width: 48px;
  height: 48px;
  background: #f0f9ff;
  border: 1px solid #e0f2fe;
  color: #0284c7;
  border-radius: 14px;
}
.machine-card h3,
.booking-card h3 {
  font-size: 18px;
  font-weight: 800;
}
.muted {
  font-size: 13px;
  color: #64748b;
  line-height: 1.8;
}
.day-track {
  position: relative;
  margin-top: 24px;
  height: 12px;
  border-radius: 8px;
  background: repeating-linear-gradient(
    to right,
    #f1f5f9 0,
    #f1f5f9 calc(25% - 1px),
    #cbd5e1 calc(25% - 1px),
    #cbd5e1 25%
  );
  overflow: hidden;
}
.day-track i {
  position: absolute;
  top: 0;
  height: 100%;
  background: #38bdf8;
  border-radius: 3px;
}
.track-labels {
  display: flex;
  justify-content: space-between;
  color: #94a3b8;
  font-size: 10px;
  margin-top: 6px;
}
.empty-slots {
  padding: 24px 0;
  text-align: center;
  color: #94a3b8;
  font-size: 13px;
}
.slot-list {
  list-style: none;
  padding: 14px 0;
  margin: 0;
  flex: 1;
}
.slot-list li {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
  padding: 9px 0;
  border-bottom: 1px solid #f1f5f9;
  font-size: 12px;
}
.slot-list li span:first-child {
  width: 100%;
  color: #64748b;
}
.slot-list strong {
  overflow-wrap: anywhere;
  flex: 1;
  font-size: 13px;
  font-weight: 600;
}
.reserve-button {
  width: 100%;
  margin-top: auto;
}
.rule-note {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-top: 24px;
  padding: 18px;
  border: 1px solid #bae6fd;
  border-radius: 18px;
  background: #f0f9ff;
  color: #075985;
  font-size: 13px;
  line-height: 1.8;
}
.rule-note > .el-icon {
  flex-shrink: 0;
  margin-top: 4px;
}
.rule-note p {
  margin-top: 5px;
}
.state-panel {
  text-align: center;
  padding: 48px 16px;
  color: #64748b;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 18px;
}
.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px 22px;
}
.form-grid :deep(.el-select),
.form-grid :deep(.el-date-editor) {
  width: 100%;
}
.form-tip {
  margin-bottom: 20px;
}
.identity-strip {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  padding: 16px 18px;
  margin-bottom: 24px;
  border: 1px solid #a7f3d0;
  border-radius: 16px;
  background: #ecfdf5;
  font-size: 14px;
  color: #065f46;
}
.identity-modes {
  margin-bottom: 24px;
}
.booking-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.booking-card {
  padding: 20px;
  border: 1px solid #e2e8f0;
  background: #fff;
  border-radius: 20px;
}
.booking-heading {
  display: flex;
  align-items: start;
  justify-content: space-between;
  gap: 12px;
}
.booking-heading p {
  font-size: 14px;
  color: #64748b;
  margin-top: 7px;
  line-height: 1.7;
}
.handover {
  margin: 14px 0 8px;
  padding: 10px 12px;
  border-radius: 10px;
  background: #f8fafc;
  font-size: 13px;
  color: #475569;
  line-height: 1.7;
}
.booking-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 18px;
}
.booking-actions .el-button + .el-button {
  margin-left: 0;
}
.portal-footer {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 12px;
  font-size: 12px;
  color: #94a3b8;
  padding: 2px 0 10px;
}
.portal-footer a {
  color: #64748b;
  text-decoration: none;
}
.portal-footer a:hover {
  color: #0284c7;
}
.incident-note {
  line-height: 1.8;
  font-size: 14px;
  color: #64748b;
  margin-bottom: 16px;
}
:deep(.el-form-item__label) {
  font-weight: 600;
  color: #334155;
}
:deep(.el-input__wrapper),
:deep(.el-select__wrapper) {
  border-radius: 10px;
}
:deep(.el-button) {
  border-radius: 10px;
}
@media (max-width: 900px) {
  .portal-hero {
    grid-template-columns: 1fr;
  }
  .hero-summary {
    max-width: none;
  }
  .machine-grid {
    grid-template-columns: 1fr;
  }
  .machine-card {
    padding: 20px;
  }
  .hero-title h1 {
    font-size: 32px;
  }
  .machine-head {
    margin-bottom: 12px;
  }
}
@media (max-width: 600px) {
  .printer-page {
    padding: 20px 12px;
  }
  .printer-shell {
    gap: 18px;
  }
  .portal-hero {
    padding: 22px 18px;
    gap: 20px;
  }
  .hero-title {
    gap: 12px;
  }
  .hero-title img {
    width: 48px;
    height: 48px;
  }
  .hero-title h1 {
    font-size: 27px;
    letter-spacing: -0.5px;
  }
  .panel-body {
    padding: 20px 16px;
  }
  .surface-header {
    padding: 12px;
  }
  .segments {
    grid-template-columns: repeat(2, 1fr);
  }
  .segments button {
    font-size: 14px;
    min-height: 44px;
  }
  .section-heading {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  .section-heading :deep(.el-date-editor) {
    width: 100%;
  }
  .section-heading h2 {
    font-size: 20px;
  }
  .form-grid {
    grid-template-columns: 1fr;
    gap: 0;
  }
  .booking-heading {
    flex-wrap: wrap;
  }
  .booking-actions .el-button {
    flex: 1;
    min-width: 120px;
  }
  .identity-strip {
    padding: 14px;
  }
  .booking-card {
    padding: 16px;
  }
  .rule-note {
    padding: 14px;
  }
}
</style>
