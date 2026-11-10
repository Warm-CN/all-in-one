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
          维护状态会阻止新增预约与签到。恢复前请确认设备安全，并检查已有预约安排。
        </p>
      </section>
      <section class="admin-card">
        <h2>预约与登记设置</h2>
        <el-form label-position="top" @submit.prevent="save"
          ><div class="setting-toggles">
            <el-form-item label="开放新队伍登记"
              ><el-switch
                v-model="settings.registration_enabled" /></el-form-item
            ><el-form-item label="限制预约开始时间"
              ><el-switch v-model="settings.opening_hours_enabled"
            /></el-form-item>
          </div>
          <p class="hint">
            仅约束预约开始节点；打印结束时间可以超过办公室关闭时间。修改后影响新预约，不会取消已有预约。
          </p>
          <div v-if="settings.opening_hours_enabled" class="hours-list">
            <div
              v-for="(hour, index) in settings.opening_hours"
              :key="index"
              class="hour-row"
            >
              <el-select v-model="hour.weekday" aria-label="开放星期"
                ><el-option
                  v-for="(name, day) in weekdays"
                  :key="day"
                  :label="name"
                  :value="day" /></el-select
              ><el-time-select
                v-model="hour.start"
                start="00:00"
                end="23:45"
                step="00:15"
                placeholder="开放时间"
              /><span>至</span
              ><el-time-select
                v-model="hour.end"
                start="00:15"
                end="23:45"
                step="00:15"
                placeholder="关闭时间"
              /><el-button
                type="danger"
                text
                @click="settings.opening_hours.splice(index, 1)"
                >移除</el-button
              >
            </div>
            <el-button
              plain
              @click="
                settings.opening_hours.push({
                  weekday: 0,
                  start: '09:00',
                  end: '18:00',
                })
              "
              >添加开放时段</el-button
            >
          </div>
          <div class="config-grid">
            <el-form-item label="赛事模块标识"
              ><el-input
                v-model="settings.module_key"
                placeholder="如 bambu_cup"
                maxlength="100" /></el-form-item
            ><el-form-item label="更新报名邀请码（留空则保留原值）"
              ><el-input
                v-model="registrationCode"
                type="password"
                show-password
                autocomplete="new-password"
                placeholder="新队伍登记时填写"
                maxlength="72"
            /></el-form-item>
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
          <h2>设备异常记录</h2>
          <el-button :loading="incidentLoading" @click="loadIncidents"
            >刷新记录</el-button
          >
        </div>
        <p class="hint">
          异常关联上一实际使用记录。请结合现场情况核查责任，处理记录会保留；设备恢复需在上方单独操作。
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
                >上一实际使用队伍：<strong>{{
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
import { onMounted, reactive, ref } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { printerApi } from "@/api/printers";
const loading = ref(true),
  incidentLoading = ref(false),
  error = ref(""),
  config = ref(null),
  incidents = ref([]),
  busy = ref(""),
  registrationCode = ref("");
const settings = reactive({
  registration_enabled: false,
  opening_hours_enabled: false,
  opening_hours: [],
  module_key: "bambu_cup",
});
const weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"];
async function load() {
  loading.value = true;
  error.value = "";
  try {
    config.value = await printerApi.adminConfig();
    Object.assign(settings, {
      registration_enabled: config.value.registration_enabled,
      opening_hours_enabled: config.value.opening_hours_enabled,
      opening_hours: (config.value.opening_hours || []).map((h) => ({ ...h })),
      module_key: config.value.module_key,
    });
    await loadIncidents();
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
        ? "暂停后该设备无法新增预约或签到，已有预约仍会保留。确认暂停？"
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
  if (!settings.module_key?.trim())
    return ElMessage.warning("请填写赛事模块标识");
  if (settings.opening_hours_enabled && !settings.opening_hours.length)
    return ElMessage.warning("启用开始时间限制时，请至少配置一个开放时段");
  if (
    settings.opening_hours.some((h) => !h.start || !h.end || h.start >= h.end)
  )
    return ElMessage.warning(
      "每个开放时段的结束时间须晚于开始时间；跨夜请拆成两天配置",
    );
  if (registrationCode.value && registrationCode.value.length < 8)
    return ElMessage.warning("报名邀请码至少需要8个字符");
  busy.value = "config";
  try {
    await printerApi.saveConfig({
      ...settings,
      ...(registrationCode.value
        ? { registration_code: registrationCode.value }
        : {}),
    });
    registrationCode.value = "";
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
  config.value?.printers.find((p) => p.id === id)?.name || `打印机 ${id}`;
const formatTime = (value) =>
  value ? String(value).replace("T", " ").slice(0, 16) : "—";
onMounted(load);
</script>

<style scoped>
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
.setting-toggles {
  display: flex;
  gap: 40px;
}
.hours-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin: 22px 0;
}
.hour-row {
  display: flex;
  gap: 10px;
  align-items: center;
}
.hour-row > .el-select {
  max-width: 120px;
}
.hour-row :deep(.el-input) {
  min-width: 100px;
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
  .hour-row {
    flex-wrap: wrap;
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
  .setting-toggles {
    gap: 20px;
  }
  .hour-row > .el-select {
    max-width: none;
    width: 100%;
  }
  .hour-row :deep(.el-time-select) {
    width: calc(50% - 24px);
  }
  .incident-heading {
    flex-wrap: wrap;
  }
  .admin-heading h1 {
    font-size: 24px;
  }
}
</style>
