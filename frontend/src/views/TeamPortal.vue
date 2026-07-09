<template>
  <div class="apply-page w-full px-3 py-5 sm:px-6 lg:px-8 lg:py-10">
    <div class="apply-shell mx-auto flex w-full max-w-[1180px] flex-col gap-5 sm:gap-7">
      <header class="hero-panel grid w-full gap-5 rounded-[28px] px-4 py-5 sm:px-6 sm:py-7 lg:grid-cols-[minmax(0,1fr)_320px] lg:items-center lg:px-8 lg:py-8">
        <div class="min-w-0">
          <div class="hero-badge-row mb-3 flex flex-wrap items-center justify-center gap-2 sm:justify-start">
            <span class="hero-badge">{{ currentEvent ? (currentEvent.cup_type === 'telecom' ? 'TELECOM CUP' : 'WIRELESS CUP') : 'COMPETITION PORTAL' }}</span>
            <span class="hero-badge hero-badge-alt">TEAM PORTAL</span>
          </div>
          <div class="flex flex-col items-center gap-3 text-center sm:flex-row sm:text-left">
            <img src="@/assets/images/logo.png" alt="Logo" class="h-16 w-auto shrink-0 object-contain sm:h-20" />
            <div class="flex min-w-0 items-center gap-3">
              <div class="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-amber-50 text-amber-600 shadow-sm">
                <el-icon :size="16"><Trophy /></el-icon>
              </div>
              <div class="min-w-0">
                <h1 class="break-words text-3xl font-black leading-tight text-slate-950 sm:text-4xl lg:text-5xl">{{ currentEvent?.display_title || currentEvent?.name || '赛事报名与组队中心' }}</h1>
                <p class="mt-3 max-w-3xl text-base leading-7 text-slate-600 sm:text-lg">公开报名、修改队伍、修改选题、查询验收安排统一在这里完成</p>
              </div>
            </div>
          </div>
        </div>

        <div class="hero-status rounded-2xl border border-slate-200/80 bg-white/82 p-4 shadow-[0_16px_38px_-32px_rgba(15,23,42,0.36)]">
          <div class="text-xs font-semibold uppercase text-slate-400">当前比赛</div>
          <div class="mt-3 break-words text-lg font-black leading-6 text-slate-900">{{ currentEvent?.display_title || currentEvent?.name || '尚未开启' }}</div>
          <div class="mt-2 text-sm leading-6 text-slate-500">
            {{ currentEvent ? (signupStatus.signup_open ? '报名页面已开放，可提交组队信息' : '报名页面暂未开放，可查询队伍信息') : '请等待管理员设置正在进行的比赛' }}
          </div>
        </div>
      </header>

      <section class="glass-card mx-auto w-full overflow-hidden rounded-[28px] border border-white/70">
        <div class="surface-header border-b border-slate-200/70 bg-white/75 p-3 sm:p-4 lg:p-5">
          <div class="native-segment mx-auto grid max-w-3xl grid-cols-1 rounded-2xl border border-slate-200/80 bg-slate-50 p-1 sm:grid-cols-3">
            <button
              class="tab-button rounded-xl px-3 py-3 text-center text-base font-semibold transition"
              :class="activeTab === 'signup' ? 'segment-active' : 'text-slate-500 hover:text-slate-800'"
              @click="handleTabSwitch('signup')"
            >
              我要组队报名
            </button>
            <button
              class="tab-button rounded-xl px-3 py-3 text-center text-base font-semibold transition"
              :class="activeTab === 'topic' ? 'segment-active' : 'text-slate-500 hover:text-slate-800'"
              @click="handleTabSwitch('topic')"
            >
              修改选题
            </button>
            <button
              class="tab-button rounded-xl px-3 py-3 text-center text-base font-semibold transition"
              :class="activeTab === 'query' ? 'segment-active' : 'text-slate-500 hover:text-slate-800'"
              @click="handleTabSwitch('query')"
            >
              队伍查询/修改信息
            </button>
          </div>
        </div>

        <div class="p-4 sm:p-6 lg:p-8">
          <el-alert
            v-if="!currentEvent"
            type="warning"
            :closable="false"
            class="mb-5"
            title="当前没有进行中的比赛，请联系管理员在赛事中心设置“正在比赛”后再进行报名。"
          />

          <div v-show="activeTab === 'signup'" class="mx-auto w-full">
            <el-alert
              v-if="currentEvent && !signupStatus.signup_open"
              type="info"
              :closable="false"
              class="mb-5"
              title="当前比赛报名页面暂未开放，请等待管理员开放后再提交组队报名。"
            />
            <el-form ref="signupFormRef" :model="signupForm" :rules="signupRules" label-position="top" size="large" class="native-form">
              <template v-if="!compactSignupMode">
                <div class="form-section">
                  <div class="section-kicker">队伍与队长信息</div>
                  <div class="grid grid-cols-1 gap-x-5 gap-y-3 md:grid-cols-2 lg:gap-y-4">
                    <el-form-item label="队伍名称" prop="team_name">
                      <el-input v-model="signupForm.team_name" placeholder="请输入队伍名称" />
                    </el-form-item>
                    <el-form-item label="队长姓名" prop="captain_name">
                      <el-input v-model="signupForm.captain_name" />
                    </el-form-item>
                    <el-form-item label="队长学号（12位）" prop="captain_student_id">
                      <el-input v-model="signupForm.captain_student_id" />
                    </el-form-item>
                    <el-form-item label="队长手机号" prop="captain_phone">
                      <el-input v-model="signupForm.captain_phone" />
                    </el-form-item>
                    <el-form-item label="队长邮箱" prop="captain_email">
                      <el-input v-model="signupForm.captain_email" />
                    </el-form-item>
                    <el-form-item label="队长学院" prop="captain_college">
                      <el-input v-model="signupForm.captain_college" placeholder="如：电子与信息学院" />
                    </el-form-item>
                    <el-form-item label="队长专业班级" prop="captain_major_class" class="md:col-span-2">
                      <el-input v-model="signupForm.captain_major_class" placeholder="如：信息工程x班" />
                    </el-form-item>
                  </div>
                </div>

                <div class="form-section mt-4">
                  <div class="section-kicker">队员信息（最多2人，可不填）</div>
                  <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
                    <div v-for="(member, idx) in signupForm.members" :key="idx" class="member-card rounded-2xl border border-slate-200/80 bg-white/90 p-4">
                      <h4 class="mb-3 font-semibold text-slate-700">队员 {{ idx + 1 }}</h4>
                      <div class="grid grid-cols-1 gap-3 sm:grid-cols-2">
                        <el-input v-model="member.name" placeholder="姓名（可留空）" class="sm:col-span-1" />
                        <el-input v-model="member.student_id" placeholder="学号（12位，可留空）" class="sm:col-span-1" />
                        <el-input v-model="member.phone" placeholder="手机号（可留空）" class="sm:col-span-1" />
                        <el-input v-model="member.email" placeholder="邮箱（可留空）" class="sm:col-span-1" />
                        <el-input v-model="member.college" placeholder="学院（可留空）" class="sm:col-span-1" />
                        <el-input v-model="member.major_class" placeholder="专业班级（可留空）" class="sm:col-span-1" />
                      </div>
                    </div>
                  </div>
                </div>
              </template>

              <template v-else>
                <el-collapse v-model="signupCollapse" class="zoom-collapse form-section">
                  <el-collapse-item name="basic" title="队伍基础信息">
                    <div class="grid grid-cols-1 gap-3 md:grid-cols-2">
                      <el-form-item label="队伍名称" prop="team_name">
                        <el-input v-model="signupForm.team_name" placeholder="请输入队伍名称" />
                      </el-form-item>
                    </div>
                  </el-collapse-item>

                  <el-collapse-item name="captain" title="队长信息">
                    <div class="grid grid-cols-1 gap-3 md:grid-cols-2">
                      <el-form-item label="队长姓名" prop="captain_name">
                        <el-input v-model="signupForm.captain_name" />
                      </el-form-item>
                      <el-form-item label="队长学号（12位）" prop="captain_student_id">
                        <el-input v-model="signupForm.captain_student_id" />
                      </el-form-item>
                      <el-form-item label="队长手机号" prop="captain_phone">
                        <el-input v-model="signupForm.captain_phone" />
                      </el-form-item>
                      <el-form-item label="队长邮箱" prop="captain_email">
                        <el-input v-model="signupForm.captain_email" />
                      </el-form-item>
                      <el-form-item label="队长学院" prop="captain_college">
                        <el-input v-model="signupForm.captain_college" placeholder="如：电子与信息学院" />
                      </el-form-item>
                      <el-form-item label="队长专业班级" prop="captain_major_class">
                        <el-input v-model="signupForm.captain_major_class" placeholder="如：信息工程x班" />
                      </el-form-item>
                    </div>
                  </el-collapse-item>

                  <el-collapse-item v-for="(member, idx) in signupForm.members" :key="`collapse-member-${idx}`" :name="`member-${idx}`" :title="`队员 ${idx + 1} 信息（可不填）`">
                    <div class="grid grid-cols-1 gap-3 md:grid-cols-2">
                      <el-input v-model="member.name" placeholder="姓名（可留空）" />
                      <el-input v-model="member.student_id" placeholder="学号（12位，可留空）" />
                      <el-input v-model="member.phone" placeholder="手机号（可留空）" />
                      <el-input v-model="member.email" placeholder="邮箱（可留空）" />
                      <el-input v-model="member.college" placeholder="学院（可留空）" />
                      <el-input v-model="member.major_class" placeholder="专业班级（可留空）" />
                    </div>
                  </el-collapse-item>
                </el-collapse>
              </template>

              <el-button type="primary" class="mt-7 h-12 w-full rounded-xl text-base font-semibold sm:mt-8" :loading="signupLoading" :disabled="!signupStatus.signup_open || !currentEvent" @click="submitSignup">
                提交组队报名
              </el-button>
            </el-form>
          </div>

          <div v-show="activeTab === 'topic'" class="mx-auto w-full">
            <el-form ref="topicQueryFormRef" :model="topicQueryForm" :rules="queryRules" label-position="top" size="large" class="native-form">
              <div class="form-section rounded-[24px] border border-slate-200/80 bg-white/92 p-4 shadow-[0_10px_30px_-30px_rgba(15,23,42,0.28)] sm:p-5">
                <div class="grid grid-cols-1 gap-3 md:grid-cols-2 md:gap-4">
                  <el-form-item label="先输入队长学号（12位）" prop="sid">
                    <el-input v-model="topicQueryForm.sid" />
                  </el-form-item>
                  <div class="flex items-end">
                    <el-button type="primary" class="!h-12 !w-full !rounded-2xl !px-6 text-base font-semibold" :loading="topicQueryLoading" @click="handleTopicQuery">
                      查询队伍
                    </el-button>
                  </div>
                </div>
              </div>
            </el-form>

            <div v-if="topicTeamResult" class="result-card mt-6 overflow-hidden rounded-[24px] border border-slate-200/80 bg-[linear-gradient(180deg,#ffffff_0%,#fbfdff_100%)] p-5 shadow-[0_16px_40px_-32px_rgba(15,23,42,0.18)] sm:p-6">
              <h3 class="break-words text-xl font-black text-slate-900">{{ topicTeamResult.team_name }}</h3>
              <p class="mt-2 break-words text-sm text-slate-500">队长：{{ topicTeamResult.captain_name }}（{{ topicTeamResult.captain_student_id }}）</p>
              <p class="mt-1 break-words text-sm text-slate-500">当前选题：{{ topicTeamResult.topic_title || '未选题' }}</p>

              <el-form :model="topicForm" :rules="topicRules" ref="topicFormRef" label-position="top" size="large" class="native-form mt-4">
                <div class="grid grid-cols-1 gap-x-5 gap-y-3 md:grid-cols-2 lg:gap-y-4">
                  <el-form-item label="队长学号（自动带入）" prop="captain_student_id">
                    <el-input v-model="topicForm.captain_student_id" readonly />
                  </el-form-item>
                  <el-form-item label="新题目" prop="topic_id" class="md:col-span-2">
                    <div class="space-y-2">
                      <div
                        v-for="item in topics"
                        :key="item.id"
                        class="topic-option flex flex-col gap-3 rounded-xl border px-3 py-3 transition sm:flex-row sm:items-center sm:justify-between"
                        :class="topicForm.topic_id === item.id ? 'border-sky-500 bg-sky-50' : 'border-slate-200 bg-white hover:border-slate-300'"
                      >
                        <span class="min-w-0 flex-1 break-words text-left text-sm font-medium text-slate-700">
                          {{ item.title || '未命名题目' }}
                        </span>
                        <div class="flex shrink-0 items-center gap-2">
                          <el-button
                            :type="topicForm.topic_id === item.id ? 'primary' : 'default'"
                            size="small"
                            @click="topicForm.topic_id = item.id"
                          >
                            {{ topicForm.topic_id === item.id ? '已选择' : '选择' }}
                          </el-button>
                          <el-button
                            type="primary"
                            plain
                            size="small"
                            :disabled="!resolveTopicDocumentUrl(item)"
                            @click.stop="openTopicDocument(item)"
                          >
                            下载
                          </el-button>
                        </div>
                      </div>
                      <div v-if="!topics.length" class="rounded-xl border border-dashed border-slate-300 bg-slate-50 px-3 py-4 text-sm text-slate-500">
                        暂无可选题目
                      </div>
                    </div>
                  </el-form-item>
                </div>

                <el-button type="primary" class="h-12 w-full rounded-xl text-base font-semibold" :loading="topicLoading" @click="submitTopicUpdate">
                  提交选题修改
                </el-button>
              </el-form>
            </div>
          </div>

          <div v-show="activeTab === 'query'" class="mx-auto w-full">
            <el-form ref="queryFormRef" :model="queryForm" :rules="queryRules" label-position="top" size="large" class="native-form">
              <div class="form-section rounded-[24px] border border-slate-200/80 bg-white/92 p-4 shadow-[0_10px_30px_-30px_rgba(15,23,42,0.28)] sm:p-5">
                <div class="grid grid-cols-1 gap-3 md:grid-cols-2 md:gap-4">
                  <el-form-item label="输入队员学号（12位）" prop="sid">
                    <el-input v-model="queryForm.sid" />
                  </el-form-item>
                  <div class="flex items-end">
                    <el-button type="primary" class="!h-12 !w-full !rounded-2xl !px-6 text-base font-semibold" :loading="queryLoading" @click="handleQuery">
                      查询队伍信息
                    </el-button>
                  </div>
                </div>
              </div>
            </el-form>

            <div v-if="teamResult" class="result-card mt-6 overflow-hidden rounded-[24px] border border-slate-200/80 bg-[linear-gradient(180deg,#ffffff_0%,#fbfdff_100%)] p-5 shadow-[0_16px_40px_-32px_rgba(15,23,42,0.18)] sm:p-6">
              <h3 class="break-words text-xl font-black text-slate-900">{{ teamResult.team_name }}</h3>
              <p class="mt-2 break-words text-sm text-slate-500">队长：{{ teamResult.captain_name }}（{{ teamResult.captain_student_id }}）</p>
              <p class="mt-1 break-words text-sm text-slate-500">学院/专业班级：{{ formatText(teamResult.captain_college) }} / {{ formatText(teamResult.captain_major_class) }}</p>
              <p class="mt-1 break-words text-sm text-slate-500">选题：{{ teamResult.topic_title || '未选题' }}</p>

              <el-divider content-position="left">队员信息</el-divider>
              <div v-if="teamResult.members?.length" class="space-y-2">
                <div v-for="member in teamResult.members" :key="member.id" class="overflow-hidden rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-700">
                  <div class="break-words">{{ member.name }} / {{ member.student_id }} / {{ member.phone }}</div>
                  <div class="mt-1 break-words text-xs text-slate-500">{{ member.email || '-' }} / {{ member.college || '-' }} / {{ member.major_class || '-' }}</div>
                </div>
              </div>
              <div v-else class="text-sm text-slate-500">暂无队员（仅队长）</div>

              <el-divider content-position="left">验收安排</el-divider>
              <div class="grid grid-cols-1 gap-3 md:grid-cols-2">
                <div class="rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm overflow-hidden">
                  <div class="font-semibold text-slate-700">第一次验收</div>
                  <div class="mt-1 break-words text-slate-600">时间：{{ formatText(teamResult.inspection?.first_inspection_time) }}</div>
                  <div class="break-words text-slate-600">地点：{{ formatText(teamResult.inspection?.first_inspection_location) }}</div>
                  <div class="break-words text-slate-600">备注：{{ formatText(teamResult.inspection?.first_notes) }}</div>
                </div>
                <div class="rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm overflow-hidden">
                  <div class="font-semibold text-slate-700">第二次验收</div>
                  <div class="mt-1 break-words text-slate-600">时间：{{ formatText(teamResult.inspection?.second_inspection_time) }}</div>
                  <div class="break-words text-slate-600">地点：{{ formatText(teamResult.inspection?.second_inspection_location) }}</div>
                  <div class="break-words text-slate-600">备注：{{ formatText(teamResult.inspection?.second_notes) }}</div>
                </div>
              </div>

              <div class="mt-5 flex flex-col gap-3 sm:flex-row">
                <el-button type="primary" plain class="!h-11 !rounded-2xl !px-6" :disabled="!updateStatus.info_update_open" @click="openEditDialog">
                  修改队伍信息
                </el-button>
                <el-button type="danger" plain class="!h-11 !rounded-2xl !px-6" :disabled="!updateStatus.info_update_open" @click="openDeleteDialog">
                  删除队伍
                </el-button>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>

    <el-dialog v-model="editVisible" title="修改队伍信息" width="min(860px, calc(100vw - 24px))" destroy-on-close>
      <el-form ref="editFormRef" :model="editForm" :rules="editRules" label-position="top" size="large">
        <div class="grid grid-cols-1 gap-x-4 gap-y-1 md:grid-cols-2">
          <el-form-item label="队伍名称" prop="team_name"><el-input v-model="editForm.team_name" /></el-form-item>
          <el-form-item label="赛道/组别"><el-input v-model="editForm.competition_track" /></el-form-item>
          <el-form-item label="队长姓名" prop="captain_name"><el-input v-model="editForm.captain_name" /></el-form-item>
          <el-form-item label="队长学号" prop="captain_student_id"><el-input v-model="editForm.captain_student_id" /></el-form-item>
          <el-form-item label="队长手机号" prop="captain_phone"><el-input v-model="editForm.captain_phone" /></el-form-item>
          <el-form-item label="队长邮箱"><el-input v-model="editForm.captain_email" /></el-form-item>
          <el-form-item label="队长学院" prop="captain_college"><el-input v-model="editForm.captain_college" /></el-form-item>
          <el-form-item label="队长专业班级" prop="captain_major_class"><el-input v-model="editForm.captain_major_class" /></el-form-item>
        </div>

        <el-divider content-position="left">队员信息（最多2人）</el-divider>
        <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
          <div v-for="(member, idx) in editForm.members" :key="idx" class="rounded-2xl border border-slate-200/80 bg-white/90 p-4">
            <h4 class="mb-3 font-semibold text-slate-700">队员 {{ idx + 1 }}</h4>
            <div class="space-y-3">
              <el-input v-model="member.name" placeholder="姓名（可留空）" />
              <el-input v-model="member.student_id" placeholder="学号（12位，可留空）" />
              <el-input v-model="member.phone" placeholder="手机号（可留空）" />
              <el-input v-model="member.email" placeholder="邮箱（可留空）" />
              <el-input v-model="member.college" placeholder="学院（可留空）" />
              <el-input v-model="member.major_class" placeholder="专业班级（可留空）" />
            </div>
          </div>
        </div>
      </el-form>
      <template #footer>
        <div class="flex flex-col gap-2 sm:flex-row sm:justify-end">
          <el-button @click="editVisible = false">取消</el-button>
          <el-button type="primary" :loading="savingEdit" @click="submitEdit">保存修改</el-button>
        </div>
      </template>
    </el-dialog>

    <el-dialog v-model="deleteVisible" title="删除队伍" width="min(640px, calc(100vw - 24px))" destroy-on-close>
      <el-form ref="deleteFormRef" :model="deleteForm" label-position="top" size="large">
        <el-form-item label="删除理由（至少5个字）">
          <el-input v-model="deleteForm.delete_reason" type="textarea" :rows="3" maxlength="200" show-word-limit />
        </el-form-item>
        <el-checkbox v-model="deleteForm.confirm_self_operation">我确认这是由队长本人发起的删除操作</el-checkbox>
        <el-checkbox v-model="deleteForm.confirm_members_informed" class="mt-3">我确认队伍队员均已知情并同意删除</el-checkbox>
      </el-form>
      <template #footer>
        <div class="flex flex-col gap-2 sm:flex-row sm:justify-end">
          <el-button @click="deleteVisible = false">取消</el-button>
          <el-button type="danger" :loading="deleting" @click="submitDelete">确认删除队伍</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Trophy } from '@element-plus/icons-vue'
import {
  createTeam,
  deleteTeam,
  getSignupStatus,
  getTeamBySid,
  getTeamUpdateStatus,
  getTopicStatus,
  getTopics,
  updateTeam,
  updateTeamTopic
} from '@/api/team'
import { getCurrentCompetitionEvent } from '@/api/competition'

const DEFAULT_MODULE_KEY = 'wireless_cup_2026'
const activeTab = ref('signup')
const currentEvent = ref(null)

const signupStatus = reactive({ signup_open: false, signup_close_at: null })
const topicStatus = reactive({ topic_open: false, topic_close_at: null })
const updateStatus = reactive({ info_update_open: false, info_update_close_at: null })
const topics = ref([])
const topicDocsByOptionId = ref({})

const signupFormRef = ref(null)
const topicFormRef = ref(null)
const topicQueryFormRef = ref(null)
const queryFormRef = ref(null)
const editFormRef = ref(null)

const signupLoading = ref(false)
const topicLoading = ref(false)
const topicQueryLoading = ref(false)
const queryLoading = ref(false)
const savingEdit = ref(false)
const deleting = ref(false)

const teamResult = ref(null)
const topicTeamResult = ref(null)
const compactSignupMode = ref(false)
const signupCollapse = ref(['basic', 'captain'])

const signupForm = reactive({
  team_name: '',
  captain_name: '',
  captain_student_id: '',
  captain_phone: '',
  captain_email: '',
  captain_college: '',
  captain_major_class: '',
  members: [
    { name: '', student_id: '', phone: '', email: '', college: '', major_class: '' },
    { name: '', student_id: '', phone: '', email: '', college: '', major_class: '' }
  ]
})

const topicForm = reactive({
  captain_student_id: '',
  topic_id: null
})

const topicQueryForm = reactive({ sid: '' })

const queryForm = reactive({ sid: '' })

const editVisible = ref(false)
const deleteVisible = ref(false)

const editForm = reactive({
  team_name: '',
  competition_track: '',
  captain_name: '',
  captain_student_id: '',
  captain_phone: '',
  captain_email: '',
  captain_college: '',
  captain_major_class: '',
  members: [
    { name: '', student_id: '', phone: '', email: '', college: '', major_class: '' },
    { name: '', student_id: '', phone: '', email: '', college: '', major_class: '' }
  ]
})

const deleteForm = reactive({
  delete_reason: '',
  confirm_self_operation: false,
  confirm_members_informed: false
})

const studentIdRule = { pattern: /^\d{12}$/, message: '学号必须是12位数字', trigger: 'blur' }

const signupRules = {
  team_name: [{ required: true, message: '请输入队伍名称', trigger: 'blur' }],
  captain_name: [{ required: true, message: '请输入队长姓名', trigger: 'blur' }],
  captain_student_id: [{ required: true, message: '请输入队长学号', trigger: 'blur' }, studentIdRule],
  captain_phone: [{ required: true, message: '请输入队长手机号', trigger: 'blur' }],
  captain_college: [{ required: true, message: '请输入队长学院', trigger: 'blur' }],
  captain_major_class: [{ required: true, message: '请输入队长专业班级', trigger: 'blur' }]
}

const topicRules = {
  captain_student_id: [{ required: true, message: '请输入队长学号', trigger: 'blur' }, studentIdRule],
  topic_id: [{ required: true, message: '请选择新题目', trigger: 'change' }]
}

const queryRules = {
  sid: [{ required: true, message: '请输入学号', trigger: 'blur' }, studentIdRule]
}

const editRules = {
  team_name: [{ required: true, message: '请输入队伍名称', trigger: 'blur' }],
  captain_name: [{ required: true, message: '请输入队长姓名', trigger: 'blur' }],
  captain_student_id: [{ required: true, message: '请输入队长学号', trigger: 'blur' }, studentIdRule],
  captain_phone: [{ required: true, message: '请输入队长手机号', trigger: 'blur' }],
  captain_college: [{ required: true, message: '请输入队长学院', trigger: 'blur' }],
  captain_major_class: [{ required: true, message: '请输入队长专业班级', trigger: 'blur' }]
}

const normalizeMembers = (members) => {
  const normalized = []
  for (const item of members) {
    const member = {
      name: (item.name || '').trim(),
      student_id: (item.student_id || '').trim(),
      phone: (item.phone || '').trim(),
      email: (item.email || '').trim(),
      college: (item.college || '').trim(),
      major_class: (item.major_class || '').trim()
    }
    const hasAny = Object.values(member).some(Boolean)
    if (!hasAny) continue
    const requiredOk = member.name && member.student_id && member.phone && member.college && member.major_class
    if (!requiredOk) {
      throw new Error('队员信息若填写，需完整填写姓名/学号/手机号/学院/专业班级')
    }
    if (!/^\d{12}$/.test(member.student_id)) {
      throw new Error('队员学号必须是12位数字')
    }
    normalized.push(member)
  }
  if (normalized.length > 2) {
    throw new Error('队员最多2人')
  }
  return normalized
}

const handleTabSwitch = (targetTab) => {
  if (targetTab === 'topic' && !topicStatus.topic_open) {
    ElMessage.warning('选题通道还未开启，敬请期待')
    return
  }
  activeTab.value = targetTab
}

const resolveTopicDocumentUrl = (topic) => {
  if (!topic?.id) return null
  return topic.document_url || topicDocsByOptionId.value[topic.id] || null
}

const openTopicDocument = (topic) => {
  const url = resolveTopicDocumentUrl(topic)
  if (!url) {
    ElMessage.warning('当前题目暂未上传附件')
    return
  }
  window.open(url, '_blank', 'noopener')
}

const loadBaseData = async () => {
  try {
    const currentRes = await getCurrentCompetitionEvent()
    currentEvent.value = currentRes.data || null

    if (!currentEvent.value) {
      topics.value = []
      topicDocsByOptionId.value = {}
      Object.assign(signupStatus, { signup_open: false, signup_close_at: null })
      Object.assign(topicStatus, { topic_open: false, topic_close_at: null })
      Object.assign(updateStatus, { info_update_open: false, info_update_close_at: null })
      return
    }

    const moduleKey = currentEvent.value.module_key || DEFAULT_MODULE_KEY
    const [signupRes, topicRes, updateRes, topicsRes] = await Promise.all([
      getSignupStatus({ module_key: moduleKey }),
      getTopicStatus({ module_key: moduleKey }),
      getTeamUpdateStatus({ module_key: moduleKey }),
      getTopics({ only_active: true, module_key: moduleKey })
    ])

    Object.assign(signupStatus, signupRes.data || {})
    Object.assign(topicStatus, topicRes.data || {})
    Object.assign(updateStatus, updateRes.data || {})
    topics.value = Array.isArray(topicsRes.data) ? topicsRes.data : []

    const eventTopicMap = {}
    if (Array.isArray(currentEvent.value?.topics)) {
      currentEvent.value.topics.forEach((item) => {
        if (item?.topic_option_id && item?.document_url) {
          eventTopicMap[item.topic_option_id] = item.document_url
        }
      })
    }
    topicDocsByOptionId.value = eventTopicMap
  } catch (error) {
    ElMessage.error(error.response?.data?.msg || error.response?.data?.detail || '初始化失败')
  }
}

const submitSignup = async () => {
  if (!currentEvent.value?.module_key) {
    ElMessage.warning('当前没有进行中的比赛')
    return
  }

  const valid = await signupFormRef.value?.validate().catch(() => false)
  if (!valid) return
  try {
    const members = normalizeMembers(signupForm.members)
    signupLoading.value = true
    const res = await createTeam({
      ...signupForm,
      module_key: currentEvent.value.module_key,
      members
    })
    ElMessage.success(res.msg || '报名成功')
  } catch (error) {
    ElMessage.error(error.response?.data?.msg || error.message || '报名失败')
  } finally {
    signupLoading.value = false
  }
}

const submitTopicUpdate = async () => {
  if (!currentEvent.value?.module_key) {
    ElMessage.warning('当前没有进行中的比赛')
    return
  }

  if (!topicTeamResult.value?.id) {
    ElMessage.warning('请先在当前页通过学号查询队伍，再修改选题')
    return
  }
  const valid = await topicFormRef.value?.validate().catch(() => false)
  if (!valid) return

  topicLoading.value = true
  try {
    const res = await updateTeamTopic(topicTeamResult.value.id, {
      captain_student_id: topicForm.captain_student_id,
      topic_id: topicForm.topic_id,
      module_key: currentEvent.value.module_key
    })
    ElMessage.success(res.msg || '选题修改成功')
    await handleTopicQuery()
  } catch (error) {
    ElMessage.error(error.response?.data?.msg || error.response?.data?.detail || '选题修改失败')
  } finally {
    topicLoading.value = false
  }
}

const handleTopicQuery = async () => {
  const valid = await topicQueryFormRef.value?.validate().catch(() => false)
  if (!valid) return
  topicQueryLoading.value = true
  try {
    const resWithModule = await getTeamBySid(topicQueryForm.sid, {
      module_key: currentEvent.value?.module_key || DEFAULT_MODULE_KEY
    })
    topicTeamResult.value = resWithModule.data
    topicForm.captain_student_id = resWithModule.data?.captain_student_id || ''
    topicForm.topic_id = resWithModule.data?.topic_id || null
  } catch (error) {
    topicTeamResult.value = null
    ElMessage.error(error.response?.data?.msg || error.response?.data?.detail || '查询失败')
  } finally {
    topicQueryLoading.value = false
  }
}

const handleQuery = async () => {
  const valid = await queryFormRef.value?.validate().catch(() => false)
  if (!valid) return
  queryLoading.value = true
  try {
    const resWithModule = await getTeamBySid(queryForm.sid, {
      module_key: currentEvent.value?.module_key || DEFAULT_MODULE_KEY
    })
    teamResult.value = resWithModule.data
    topicForm.captain_student_id = resWithModule.data?.captain_student_id || ''
  } catch (error) {
    teamResult.value = null
    ElMessage.error(error.response?.data?.msg || error.response?.data?.detail || '查询失败')
  } finally {
    queryLoading.value = false
  }
}

const openEditDialog = () => {
  if (!teamResult.value) return
  editForm.team_name = teamResult.value.team_name || ''
  editForm.competition_track = teamResult.value.competition_track || ''
  editForm.captain_name = teamResult.value.captain_name || ''
  editForm.captain_student_id = teamResult.value.captain_student_id || ''
  editForm.captain_phone = teamResult.value.captain_phone || ''
  editForm.captain_email = teamResult.value.captain_email || ''
  editForm.captain_college = teamResult.value.captain_college || ''
  editForm.captain_major_class = teamResult.value.captain_major_class || ''

  const members = Array.isArray(teamResult.value.members) ? teamResult.value.members : []
  editForm.members[0] = members[0]
    ? {
        name: members[0].name || '',
        student_id: members[0].student_id || '',
        phone: members[0].phone || '',
        email: members[0].email || '',
        college: members[0].college || '',
        major_class: members[0].major_class || ''
      }
    : { name: '', student_id: '', phone: '', email: '', college: '', major_class: '' }
  editForm.members[1] = members[1]
    ? {
        name: members[1].name || '',
        student_id: members[1].student_id || '',
        phone: members[1].phone || '',
        email: members[1].email || '',
        college: members[1].college || '',
        major_class: members[1].major_class || ''
      }
    : { name: '', student_id: '', phone: '', email: '', college: '', major_class: '' }

  editVisible.value = true
}

const submitEdit = async () => {
  if (!teamResult.value?.id) return
  const valid = await editFormRef.value?.validate().catch(() => false)
  if (!valid) return
  savingEdit.value = true
  try {
    const members = normalizeMembers(editForm.members)
    const res = await updateTeam(teamResult.value.id, {
      ...editForm,
      members
    })
    ElMessage.success(res.msg || '修改成功')
    editVisible.value = false
    queryForm.sid = editForm.captain_student_id
    await handleQuery()
  } catch (error) {
    ElMessage.error(error.response?.data?.msg || error.message || '修改失败')
  } finally {
    savingEdit.value = false
  }
}

const openDeleteDialog = () => {
  deleteForm.delete_reason = ''
  deleteForm.confirm_self_operation = false
  deleteForm.confirm_members_informed = false
  deleteVisible.value = true
}

const submitDelete = async () => {
  if (!teamResult.value?.id) return
  if (!deleteForm.delete_reason || deleteForm.delete_reason.trim().length < 5) {
    ElMessage.warning('请填写至少5个字的删除理由')
    return
  }
  deleting.value = true
  try {
    const res = await deleteTeam(teamResult.value.id, {
      captain_student_id: teamResult.value.captain_student_id,
      captain_phone: teamResult.value.captain_phone,
      delete_reason: deleteForm.delete_reason,
      confirm_self_operation: deleteForm.confirm_self_operation,
      confirm_members_informed: deleteForm.confirm_members_informed,
      module_key: currentEvent.value?.module_key || DEFAULT_MODULE_KEY
    })
    ElMessage.success(res.msg || '删除成功')
    deleteVisible.value = false
    teamResult.value = null
  } catch (error) {
    ElMessage.error(error.response?.data?.msg || error.response?.data?.detail || '删除失败')
  } finally {
    deleting.value = false
  }
}

const formatText = (value) => value || '待安排'

const syncCompactMode = () => {
  compactSignupMode.value = window.innerWidth <= 1180
  if (!compactSignupMode.value) {
    signupCollapse.value = ['basic', 'captain']
  }
}

onMounted(() => {
  loadBaseData()
  syncCompactMode()
  window.addEventListener('resize', syncCompactMode)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', syncCompactMode)
})
</script>

<style scoped>
.glass-card {
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.96) 0%, rgba(248, 250, 252, 0.92) 100%);
  backdrop-filter: blur(8px);
  box-shadow: 0 22px 66px -44px rgba(15, 23, 42, 0.45);
  position: relative;
}

.glass-card::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: 28px;
  padding: 1px;
  background: linear-gradient(125deg, rgba(14, 165, 233, 0.5), rgba(37, 99, 235, 0.12), rgba(20, 184, 166, 0.36));
  mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  pointer-events: none;
}

.apply-page {
  display: flex;
  justify-content: center;
  min-height: 100%;
  background:
    linear-gradient(135deg, #eef7ff 0%, #f8fafc 48%, #ecfdf8 100%);
}

.hero-panel {
  position: relative;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.7);
  background:
    linear-gradient(135deg, rgba(255, 255, 255, 0.96), rgba(240, 249, 255, 0.9) 58%, rgba(236, 253, 245, 0.86));
  box-shadow: 0 24px 58px -44px rgba(15, 23, 42, 0.45);
}

.hero-panel::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, rgba(14, 165, 233, 0.08), transparent 36%, rgba(20, 184, 166, 0.08));
  pointer-events: none;
}

.hero-panel > * {
  position: relative;
  z-index: 1;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 9999px;
  border: 1px solid rgba(14, 165, 233, 0.28);
  background: rgba(14, 165, 233, 0.12);
  color: #0f766e;
  font-size: 12px;
  font-weight: 700;
  padding: 6px 12px;
}

.hero-badge-alt {
  border-color: rgba(249, 115, 22, 0.3);
  background: rgba(249, 115, 22, 0.12);
  color: #9a3412;
}

.native-segment .segment-active {
  background: linear-gradient(145deg, #ffffff 0%, #f0f9ff 100%);
  color: #0f172a;
  box-shadow: 0 10px 22px -14px rgba(14, 116, 144, 0.45);
}

.native-segment button {
  white-space: normal;
  line-height: 1.25;
}

.surface-header {
  backdrop-filter: blur(8px);
}

.tab-button {
  min-height: 48px;
}

.status-card,
.form-section,
.member-card,
.result-card,
.topic-option {
  min-width: 0;
}

.status-card {
  box-shadow: 0 12px 28px -28px rgba(15, 23, 42, 0.38);
}

.form-section {
  border: 1px solid rgba(226, 232, 240, 0.84);
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.74);
  padding: 18px;
}

.section-kicker {
  margin-bottom: 14px;
  color: #0f766e;
  font-size: 12px;
  font-weight: 800;
  text-transform: uppercase;
}

.native-form :deep(.el-form-item) {
  margin-bottom: 14px;
}

.native-form :deep(.el-input__wrapper),
.native-form :deep(.el-select__wrapper) {
  min-height: 42px;
}

.hero-panel h1 {
  line-height: 1.15;
}

.hero-panel p {
  line-height: 1.7;
}

.zoom-collapse {
  background: transparent;
}

.zoom-collapse :deep(.el-collapse-item) {
  margin-bottom: 12px;
  border: 1px solid rgba(148, 163, 184, 0.25);
  border-radius: 16px;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.9);
}

.zoom-collapse :deep(.el-collapse-item__header) {
  min-height: 48px;
  padding: 0 14px;
  font-weight: 700;
  color: #0f172a;
  border-bottom: none;
  background: linear-gradient(180deg, rgba(248, 250, 252, 0.96), rgba(241, 245, 249, 0.96));
}

.zoom-collapse :deep(.el-collapse-item__wrap) {
  border-bottom: none;
}

.zoom-collapse :deep(.el-collapse-item__content) {
  padding: 14px 14px 4px;
}

@media (min-width: 1024px) {
  .native-form :deep(.el-form-item) {
    margin-bottom: 18px;
  }
}

@media (max-width: 768px) {
  .hero-badge {
    font-size: 10px;
  }
}

@media (max-width: 640px) {
  .apply-page {
    padding-left: 12px;
    padding-right: 12px;
  }

  .hero-panel,
  .glass-card {
    border-radius: 22px;
  }

  .hero-status,
  .form-section {
    padding: 14px;
  }

  .tab-button {
    min-height: 44px;
  }
}
</style>
