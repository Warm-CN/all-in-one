<template>
  <div class="event-management-page flex h-full min-h-0 flex-col gap-5 pb-3 sm:gap-6">
    <section class="rounded-2xl border border-slate-200 bg-white px-4 py-5 shadow-[0_14px_34px_-30px_rgba(15,23,42,0.22)] sm:px-6 sm:py-6">
      <div class="flex min-w-0 flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div class="min-w-0">
          <div class="flex items-center gap-3">
            <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-50 text-blue-600 shadow-sm">
              <el-icon :size="16"><Trophy /></el-icon>
            </div>
            <div>
              <span class="inline-flex max-w-full items-center rounded-full bg-blue-50 px-3 py-1 text-[11px] font-semibold tracking-[0.16em] text-blue-600">
                EVENTS ADMIN
              </span>
              <h2 class="mt-3 text-[1.75rem] font-black tracking-tight text-slate-900 sm:text-[2.15rem]">
                赛事管理
              </h2>
            </div>
          </div>
          <p class="mt-2 max-w-3xl text-sm leading-6 text-slate-500">
            管理比赛条目、当前比赛、报名页面展示、选题配置和队伍入口。
          </p>
        </div>

        <div class="grid w-full grid-cols-1 gap-2 sm:w-auto sm:grid-cols-2 lg:flex lg:justify-end">
          <el-button type="primary" :icon="Plus" :loading="creating" @click="openCreateDialog">
            新建比赛
          </el-button>
          <el-button :icon="Refresh" :loading="loading" @click="fetchDashboard">
            刷新
          </el-button>
        </div>
      </div>
    </section>

    <section class="rounded-2xl border border-slate-200 bg-white p-4 shadow-[0_12px_28px_-30px_rgba(15,23,42,0.2)] sm:p-5">
      <div class="mb-4 flex min-w-0 items-center justify-between gap-3">
        <div class="min-w-0">
          <h3 class="text-lg font-bold text-slate-900">正在进行的比赛</h3>
          <p class="mt-1 text-sm text-slate-500">当前对外报名入口会优先使用该比赛。</p>
        </div>
        <el-tag v-if="currentEvent" type="success" effect="light">进行中</el-tag>
      </div>

      <div v-if="currentEvent" class="grid grid-cols-1 gap-4 lg:grid-cols-[minmax(0,1fr)_auto] lg:items-center">
        <div class="min-w-0">
          <div class="flex min-w-0 flex-wrap items-center gap-2">
            <el-tag :type="cupTagType(currentEvent.cup_type)" effect="plain">{{ cupLabel(currentEvent.cup_type) }}</el-tag>
            <el-tag :type="currentEvent.signup_open ? 'success' : 'info'" effect="light">
              {{ currentEvent.signup_open ? '报名页开放' : '报名页关闭' }}
            </el-tag>
            <h4 class="min-w-0 text-xl font-bold leading-snug text-slate-900">{{ currentEvent.name }}</h4>
          </div>
          <p class="mt-2 text-sm leading-6 text-slate-500 break-words">
            报名页标题：{{ currentEvent.display_title || currentEvent.portal_title || currentEvent.name }}
          </p>
          <p class="text-xs leading-6 text-slate-400 break-all">模块标识：{{ currentEvent.module_key }}</p>
        </div>

        <div class="grid min-w-0 grid-cols-2 gap-2 sm:grid-cols-4 lg:min-w-[420px]">
          <div class="rounded-xl bg-slate-50 px-3 py-3 text-center">
            <div class="text-xs font-semibold text-slate-500">队伍</div>
            <div class="mt-1 text-lg font-black text-slate-900">{{ currentEvent.team_count || 0 }}</div>
          </div>
          <div class="rounded-xl bg-slate-50 px-3 py-3 text-center">
            <div class="text-xs font-semibold text-slate-500">报名人数</div>
            <div class="mt-1 text-lg font-black text-slate-900">{{ currentEvent.total_people || 0 }}</div>
          </div>
          <div class="rounded-xl bg-slate-50 px-3 py-3 text-center">
            <div class="text-xs font-semibold text-slate-500">选题</div>
            <div class="mt-1 text-lg font-black text-slate-900">{{ currentEvent.topic_count || 0 }}</div>
          </div>
          <div class="rounded-xl bg-slate-50 px-3 py-3 text-center">
            <div class="text-xs font-semibold text-slate-500">计划题数</div>
            <div class="mt-1 text-lg font-black text-slate-900">{{ currentEvent.planned_topic_count || 0 }}</div>
          </div>
        </div>

        <div class="flex flex-col gap-2 sm:flex-row lg:col-span-2 lg:justify-end">
          <el-button type="primary" :icon="Right" @click="selectEvent(currentEvent)">
            进入管理
          </el-button>
        </div>
      </div>

      <div v-else class="rounded-xl border border-dashed border-slate-300 bg-slate-50 px-4 py-8 text-center text-sm text-slate-500">
        暂无正在进行的比赛
      </div>
    </section>

    <div class="grid min-h-0 grid-cols-1 gap-5 xl:grid-cols-5">
      <section class="rounded-2xl border border-slate-200 bg-white p-4 shadow-[0_12px_28px_-30px_rgba(15,23,42,0.18)] sm:p-5 xl:col-span-2">
        <div class="mb-4 flex min-w-0 items-center justify-between gap-3">
          <div class="min-w-0">
            <h3 class="text-lg font-bold text-slate-900">全部比赛</h3>
            <p class="mt-1 text-sm text-slate-500">共 {{ events.length }} 场</p>
          </div>
        </div>

        <div v-if="loading" class="space-y-3">
          <el-skeleton v-for="item in 3" :key="item" animated>
            <template #template>
              <div class="rounded-xl border border-slate-100 p-4">
                <el-skeleton-item variant="h3" class="!w-3/5" />
                <el-skeleton-item variant="text" class="!mt-3 !w-full" />
                <el-skeleton-item variant="text" class="!mt-2 !w-4/5" />
              </div>
            </template>
          </el-skeleton>
        </div>

        <div v-else-if="!events.length" class="rounded-xl border border-dashed border-slate-300 bg-slate-50 px-4 py-8 text-center text-sm text-slate-500">
          暂无比赛条目
        </div>

        <div v-else class="space-y-3">
          <article
            v-for="item in events"
            :key="item.id"
            role="button"
            tabindex="0"
            class="event-card rounded-xl border p-4"
            :class="selectedEvent?.id === item.id ? 'border-blue-300 bg-blue-50/70' : 'border-slate-200 bg-white hover:border-blue-200 hover:bg-blue-50/30'"
            @click="selectEvent(item)"
            @keyup.enter="selectEvent(item)"
          >
            <div class="flex min-w-0 flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
              <div class="min-w-0">
                <div class="flex min-w-0 flex-wrap items-center gap-2">
                  <el-tag :type="cupTagType(item.cup_type)" effect="plain">{{ cupLabel(item.cup_type) }}</el-tag>
                  <el-tag :type="item.is_current ? 'success' : 'info'" effect="light">
                    {{ item.is_current ? '进行中' : '未进行' }}
                  </el-tag>
                  <el-tag :type="item.signup_open ? 'success' : 'info'" effect="light">
                    {{ item.signup_open ? '报名页开放' : '报名页关闭' }}
                  </el-tag>
                </div>
                <h4 class="mt-3 text-base font-bold leading-snug text-slate-900 break-words">{{ item.name }}</h4>
                <p class="mt-1 text-xs leading-5 text-slate-500 break-words">
                  报名页标题：{{ item.display_title || item.portal_title || item.name }}
                </p>
                <p class="text-xs leading-5 text-slate-400 break-all">模块：{{ item.module_key }}</p>
              </div>
            </div>

            <div class="mt-4 grid grid-cols-3 gap-2">
              <div class="rounded-lg bg-slate-50 px-2 py-2 text-center">
                <div class="text-[11px] font-semibold text-slate-500">队伍</div>
                <div class="mt-1 text-sm font-black text-slate-900">{{ item.team_count || 0 }}</div>
              </div>
              <div class="rounded-lg bg-slate-50 px-2 py-2 text-center">
                <div class="text-[11px] font-semibold text-slate-500">人数</div>
                <div class="mt-1 text-sm font-black text-slate-900">{{ item.total_people || 0 }}</div>
              </div>
              <div class="rounded-lg bg-slate-50 px-2 py-2 text-center">
                <div class="text-[11px] font-semibold text-slate-500">选题</div>
                <div class="mt-1 text-sm font-black text-slate-900">{{ item.topic_count || 0 }}</div>
              </div>
            </div>

            <div class="mt-3 space-y-1 text-xs leading-5 text-slate-500">
              <p class="break-words">报名：{{ formatRange(item.signup_start_at, item.signup_end_at) }}</p>
              <p class="break-words">选题：{{ formatRange(item.topic_open_at, item.topic_end_at) }}</p>
              <p class="break-words">赛期：{{ formatRange(item.cycle_start_at, item.cycle_end_at) }}</p>
            </div>

            <p class="mt-4 text-xs font-semibold text-blue-600">点击卡片进入管理</p>
          </article>
        </div>
      </section>

      <section
        v-loading="detailLoading"
        class="rounded-2xl border border-slate-200 bg-white p-4 shadow-[0_12px_28px_-30px_rgba(15,23,42,0.18)] sm:p-5 xl:col-span-3"
      >
        <div v-if="!selectedEvent" class="flex min-h-[420px] items-center justify-center rounded-xl border border-dashed border-slate-300 bg-slate-50 px-4 py-10 text-center">
          <div class="max-w-sm">
            <h3 class="text-lg font-bold text-slate-900">选择比赛进行管理</h3>
            <p class="mt-2 text-sm leading-6 text-slate-500">点击左侧比赛条目后，可维护基础信息、当前状态、选题和队伍管理入口。</p>
          </div>
        </div>

        <div v-else class="min-w-0">
          <div class="flex min-w-0 flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
            <div class="min-w-0">
              <div class="flex flex-wrap items-center gap-2">
                <el-tag :type="cupTagType(selectedEvent.cup_type)" effect="plain">{{ cupLabel(selectedEvent.cup_type) }}</el-tag>
                <el-tag :type="selectedEvent.is_current ? 'success' : 'info'" effect="light">
                  {{ selectedEvent.is_current ? '进行中' : '未进行' }}
                </el-tag>
                <el-tag :type="selectedEvent.signup_open ? 'success' : 'info'" effect="light">
                  {{ selectedEvent.signup_open ? '报名页开放' : '报名页关闭' }}
                </el-tag>
              </div>
              <h3 class="mt-3 text-2xl font-black leading-snug text-slate-900 break-words">{{ selectedEvent.name }}</h3>
              <p class="mt-1 text-xs leading-5 text-slate-400 break-all">模块标识：{{ selectedEvent.module_key }}</p>
            </div>

            <div class="grid w-full grid-cols-1 gap-2 sm:grid-cols-3 lg:w-auto">
              <el-button type="primary" :icon="Right" @click="goTeamsCenter(selectedEvent)">
                队伍管理
              </el-button>
              <el-button
                :type="selectedEvent.signup_open ? 'danger' : 'success'"
                :loading="signupOpenSavingId === selectedEvent.id"
                @click="toggleSignupOpen(selectedEvent)"
              >
                {{ selectedEvent.signup_open ? '关闭报名页面' : '开放报名页面' }}
              </el-button>
              <el-button :loading="activeSavingId === selectedEvent.id" @click="toggleEventCurrent(selectedEvent)">
                {{ selectedEvent.is_current ? '取消进行中' : '设为进行中' }}
              </el-button>
            </div>
          </div>

          <div class="mt-5 grid grid-cols-2 gap-3 sm:grid-cols-4">
            <div class="rounded-xl bg-slate-50 px-3 py-3 text-center">
              <div class="text-xs font-semibold text-slate-500">队伍</div>
              <div class="mt-1 text-xl font-black text-slate-900">{{ selectedEvent.team_count || 0 }}</div>
            </div>
            <div class="rounded-xl bg-slate-50 px-3 py-3 text-center">
              <div class="text-xs font-semibold text-slate-500">报名人数</div>
              <div class="mt-1 text-xl font-black text-slate-900">{{ selectedEvent.total_people || 0 }}</div>
            </div>
            <div class="rounded-xl bg-slate-50 px-3 py-3 text-center">
              <div class="text-xs font-semibold text-slate-500">选题</div>
              <div class="mt-1 text-xl font-black text-slate-900">{{ selectedEvent.topic_count || 0 }}</div>
            </div>
            <div class="rounded-xl bg-slate-50 px-3 py-3 text-center">
              <div class="text-xs font-semibold text-slate-500">创建时间</div>
              <div class="mt-1 text-sm font-bold leading-5 text-slate-900">{{ formatDate(selectedEvent.created_at) }}</div>
            </div>
          </div>

          <div class="event-info-panel mt-5 rounded-xl border border-slate-200 bg-slate-50/70 p-4">
            <div class="mb-4 flex min-w-0 flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
              <h4 class="text-base font-bold text-slate-900">基础信息</h4>
              <el-button type="primary" :icon="Edit" :loading="savingDetails" @click="saveEventDetails">
                保存基础信息
              </el-button>
            </div>

            <el-form :model="detailForm" label-position="top" size="large" class="form-grid">
              <div class="event-form-stack">
                <div class="grid grid-cols-1 gap-x-4 gap-y-5 md:grid-cols-2">
                <el-form-item label="比赛名称">
                  <el-input v-model="detailForm.name" maxlength="120" show-word-limit placeholder="请输入比赛名称" />
                </el-form-item>
                <el-form-item label="报名页展示名称">
                  <el-input v-model="detailForm.portal_title" maxlength="120" show-word-limit placeholder="默认同比赛名称" />
                </el-form-item>
                </div>

                <el-form-item class="max-w-full md:max-w-[320px]" label="计划题目数量">
                  <el-input-number v-model="detailForm.planned_topic_count" :min="0" :step="1" :precision="0" controls-position="right" />
                </el-form-item>

                <div class="time-pair-grid">
                <el-form-item label="比赛周期开始">
                  <el-date-picker v-model="detailForm.cycle_start_at" type="datetime" format="YYYY-MM-DD HH:mm" value-format="YYYY-MM-DDTHH:mm:ss" placeholder="选择时间" />
                </el-form-item>
                <el-form-item label="比赛周期结束">
                  <el-date-picker v-model="detailForm.cycle_end_at" type="datetime" format="YYYY-MM-DD HH:mm" value-format="YYYY-MM-DDTHH:mm:ss" placeholder="选择时间" />
                </el-form-item>
                </div>

                <div class="time-pair-grid">
                <el-form-item label="报名开始时间">
                  <el-date-picker v-model="detailForm.signup_start_at" type="datetime" format="YYYY-MM-DD HH:mm" value-format="YYYY-MM-DDTHH:mm:ss" placeholder="选择时间" />
                </el-form-item>
                <el-form-item label="报名结束时间">
                  <el-date-picker v-model="detailForm.signup_end_at" type="datetime" format="YYYY-MM-DD HH:mm" value-format="YYYY-MM-DDTHH:mm:ss" placeholder="选择时间" />
                </el-form-item>
                </div>

                <div class="time-pair-grid">
                <el-form-item label="选题开放时间">
                  <el-date-picker v-model="detailForm.topic_open_at" type="datetime" format="YYYY-MM-DD HH:mm" value-format="YYYY-MM-DDTHH:mm:ss" placeholder="选择时间" />
                </el-form-item>
                <el-form-item label="选题结束时间">
                  <el-date-picker v-model="detailForm.topic_end_at" type="datetime" format="YYYY-MM-DD HH:mm" value-format="YYYY-MM-DDTHH:mm:ss" placeholder="选择时间" />
                </el-form-item>
                </div>
              </div>
            </el-form>
          </div>

          <div class="topic-section rounded-xl border border-slate-200 bg-white p-4">
            <div class="mb-4 flex min-w-0 flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
              <div class="min-w-0">
                <h4 class="text-base font-bold text-slate-900">选题管理</h4>
                <p class="mt-1 text-sm text-slate-500">已配置 {{ selectedTopics.length }} 个选题</p>
              </div>
            </div>

            <div class="grid grid-cols-1 gap-4 lg:grid-cols-2">
              <div class="min-w-0 rounded-xl border border-slate-200 bg-slate-50/70 p-3">
                <div v-if="!selectedTopics.length" class="rounded-lg border border-dashed border-slate-300 bg-white px-4 py-8 text-center text-sm text-slate-500">
                  暂无选题
                </div>
                <div v-else class="space-y-2">
                  <button
                    v-for="topic in selectedTopics"
                    :key="topic.id"
                    type="button"
                    class="topic-row w-full rounded-lg border px-3 py-3 text-left"
                    :class="selectedTopicId === topic.id ? 'border-blue-300 bg-blue-50' : 'border-slate-200 bg-white hover:border-blue-200'"
                    @click="selectTopicForEdit(topic)"
                  >
                    <span class="block text-sm font-bold leading-5 text-slate-900 break-words">{{ topic.title }}</span>
                    <span class="mt-1 block text-xs leading-5 text-slate-500 break-words">
                      队伍 {{ topic.selected_team_count || 0 }} / 人数 {{ topic.selected_total_people || 0 }}
                    </span>
                    <span v-if="topic.description" class="mt-1 block text-xs leading-5 text-slate-500 break-words">{{ topic.description }}</span>
                    <span v-if="topic.document_name" class="mt-2 inline-flex max-w-full items-center rounded-full bg-slate-100 px-2 py-1 text-xs text-slate-500">
                      <span class="min-w-0 break-all">{{ topic.document_name }}</span>
                    </span>
                    <el-button v-if="topic.document_url" link type="primary" class="!mt-2" @click.stop="downloadTopicDocument(topic)">
                      下载文档
                    </el-button>
                  </button>
                </div>
              </div>

              <el-form :model="topicForm" label-position="top" size="large" class="form-grid topic-editor-form min-w-0">
                <div class="mb-3 flex items-center justify-between gap-2">
                  <h5 class="text-sm font-bold text-slate-900">{{ selectedTopicId ? '编辑选题' : '新增选题' }}</h5>
                  <el-button v-if="selectedTopicId" link type="primary" @click="resetTopicForm">切换为新增</el-button>
                </div>
                <el-form-item label="选题名称">
                  <el-input v-model="topicForm.title" maxlength="120" show-word-limit placeholder="请输入选题名称" />
                </el-form-item>
                <el-form-item label="选题简介">
                  <el-input v-model="topicForm.description" type="textarea" :rows="4" maxlength="500" show-word-limit placeholder="可选" />
                </el-form-item>
                <el-form-item label="选题文档">
                  <el-upload
                    class="topic-upload"
                    drag
                    action="#"
                    accept=".pdf,.doc,.docx"
                    :auto-upload="false"
                    :limit="1"
                    :file-list="topicUploadList"
                    :on-change="handleFileChange"
                    :on-remove="handleFileRemove"
                    :on-exceed="handleFileExceed"
                  >
                    <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
                    <div class="el-upload__text">拖拽文件到此处或<em>点击上传</em></div>
                    <template #tip>
                      <div class="el-upload__tip">支持 pdf、doc、docx</div>
                    </template>
                  </el-upload>
                </el-form-item>
                <el-button type="primary" class="w-full" :loading="savingTopic" @click="submitTopic">
                  {{ selectedTopicId ? '保存选题' : '添加选题' }}
                </el-button>
              </el-form>
            </div>
          </div>
        </div>
      </section>
    </div>

    <el-dialog
      v-model="createDialogVisible"
      title="新建比赛"
      width="min(900px, calc(100vw - 24px))"
      destroy-on-close
      :close-on-click-modal="false"
    >
      <el-form :model="createForm" label-position="top" size="large" class="form-grid">
        <div class="event-form-stack">
          <div class="grid grid-cols-1 gap-x-4 gap-y-5 md:grid-cols-2">
            <el-form-item label="赛事类型">
              <el-select v-model="createForm.cup_type" placeholder="选择赛事类型">
                <el-option label="无线杯" value="wireless" />
                <el-option label="电信杯" value="telecom" />
              </el-select>
            </el-form-item>
            <el-form-item label="比赛名称">
              <el-input v-model="createForm.name" maxlength="120" show-word-limit placeholder="如：2026 年无线杯" />
            </el-form-item>
            <el-form-item label="报名页展示名称">
              <el-input v-model="createForm.portal_title" maxlength="120" show-word-limit placeholder="默认同比赛名称" />
            </el-form-item>
            <el-form-item label="计划题目数量">
              <el-input-number v-model="createForm.planned_topic_count" :min="0" :step="1" :precision="0" controls-position="right" />
            </el-form-item>
          </div>

          <div class="time-pair-grid">
            <el-form-item label="比赛周期开始">
              <el-date-picker v-model="createForm.cycle_start_at" type="datetime" format="YYYY-MM-DD HH:mm" value-format="YYYY-MM-DDTHH:mm:ss" placeholder="选择时间" />
            </el-form-item>
            <el-form-item label="比赛周期结束">
              <el-date-picker v-model="createForm.cycle_end_at" type="datetime" format="YYYY-MM-DD HH:mm" value-format="YYYY-MM-DDTHH:mm:ss" placeholder="选择时间" />
            </el-form-item>
          </div>

          <div class="time-pair-grid">
            <el-form-item label="报名开始时间">
              <el-date-picker v-model="createForm.signup_start_at" type="datetime" format="YYYY-MM-DD HH:mm" value-format="YYYY-MM-DDTHH:mm:ss" placeholder="选择时间" />
            </el-form-item>
            <el-form-item label="报名结束时间">
              <el-date-picker v-model="createForm.signup_end_at" type="datetime" format="YYYY-MM-DD HH:mm" value-format="YYYY-MM-DDTHH:mm:ss" placeholder="选择时间" />
            </el-form-item>
          </div>

          <div class="time-pair-grid">
            <el-form-item label="选题开放时间">
              <el-date-picker v-model="createForm.topic_open_at" type="datetime" format="YYYY-MM-DD HH:mm" value-format="YYYY-MM-DDTHH:mm:ss" placeholder="选择时间" />
            </el-form-item>
            <el-form-item label="选题结束时间">
              <el-date-picker v-model="createForm.topic_end_at" type="datetime" format="YYYY-MM-DD HH:mm" value-format="YYYY-MM-DDTHH:mm:ss" placeholder="选择时间" />
            </el-form-item>
          </div>
        </div>
      </el-form>
      <template #footer>
        <div class="grid grid-cols-1 gap-2 sm:flex sm:justify-end">
          <el-button @click="createDialogVisible = false">取消</el-button>
          <el-button type="primary" :icon="Plus" :loading="creating" @click="submitCreate">创建比赛</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Edit, Plus, Refresh, Right, Trophy, UploadFilled } from '@element-plus/icons-vue'
import {
  createCompetitionEvent,
  createCompetitionTopic,
  getCompetitionEventDetail,
  getCompetitionEvents,
  getCurrentCompetitionEvent,
  updateCompetitionActiveState,
  updateCompetitionEvent,
  updateCompetitionSignupOpenState,
  updateCompetitionTopic,
} from '@/api/competition'

const router = useRouter()

const loading = ref(false)
const detailLoading = ref(false)
const creating = ref(false)
const savingDetails = ref(false)
const savingTopic = ref(false)
const activeSavingId = ref(null)
const signupOpenSavingId = ref(null)

const createDialogVisible = ref(false)
const events = ref([])
const currentEvent = ref(null)
const selectedEvent = ref(null)
const selectedTopicId = ref(null)
const topicFile = ref(null)
const topicUploadList = ref([])

const emptyEventForm = () => ({
  cup_type: 'wireless',
  name: '',
  portal_title: '',
  planned_topic_count: 0,
  signup_start_at: null,
  signup_end_at: null,
  topic_open_at: null,
  topic_end_at: null,
  cycle_start_at: null,
  cycle_end_at: null,
})

const createForm = reactive(emptyEventForm())
const detailForm = reactive(emptyEventForm())

const topicForm = reactive({
  title: '',
  description: '',
})

const selectedTopics = computed(() => Array.isArray(selectedEvent.value?.topics) ? selectedEvent.value.topics : [])

const datePairs = [
  ['cycle_start_at', 'cycle_end_at', '比赛周期'],
  ['signup_start_at', 'signup_end_at', '报名时间'],
  ['topic_open_at', 'topic_end_at', '选题时间'],
]

const dateTimeFormatter = new Intl.DateTimeFormat('zh-CN', {
  year: 'numeric',
  month: '2-digit',
  day: '2-digit',
  hour: '2-digit',
  minute: '2-digit',
  hour12: false,
})

const getErrorMessage = (error, fallback) => {
  const detail = error?.response?.data?.detail
  return error?.response?.data?.msg || (typeof detail === 'string' ? detail : '') || error?.message || fallback
}

const cupLabel = (type) => {
  if (type === 'telecom') return '电信杯'
  return '无线杯'
}

const cupTagType = (type) => {
  if (type === 'telecom') return 'warning'
  return 'primary'
}

const toSortableTime = (value) => {
  const time = new Date(value || 0).getTime()
  return Number.isFinite(time) ? time : 0
}

const sortEvents = (items) => {
  return [...items].sort((left, right) => toSortableTime(right.created_at) - toSortableTime(left.created_at))
}

const formatDate = (value) => {
  if (!value) return '未设置'
  const date = new Date(value)
  if (!Number.isFinite(date.getTime())) return '未设置'
  return dateTimeFormatter.format(date)
}

const formatRange = (start, end) => `${formatDate(start)} 至 ${formatDate(end)}`

const resetCreateForm = () => {
  Object.assign(createForm, emptyEventForm())
}

const syncDetailForm = (event) => {
  Object.assign(detailForm, {
    cup_type: event?.cup_type || 'wireless',
    name: event?.name || '',
    portal_title: event?.portal_title || event?.display_title || event?.name || '',
    planned_topic_count: Number(event?.planned_topic_count || 0),
    signup_start_at: event?.signup_start_at || null,
    signup_end_at: event?.signup_end_at || null,
    topic_open_at: event?.topic_open_at || null,
    topic_end_at: event?.topic_end_at || null,
    cycle_start_at: event?.cycle_start_at || null,
    cycle_end_at: event?.cycle_end_at || null,
  })
}

const validateEventForm = (form) => {
  if (!form.name.trim()) {
    ElMessage.warning('请输入比赛名称')
    return false
  }

  for (const [startKey, endKey, label] of datePairs) {
    const start = form[startKey]
    const end = form[endKey]
    if (!start || !end) continue

    const startTime = new Date(start).getTime()
    const endTime = new Date(end).getTime()
    if (Number.isFinite(startTime) && Number.isFinite(endTime) && startTime > endTime) {
      ElMessage.warning(`${label}结束时间不能早于开始时间`)
      return false
    }
  }

  return true
}

const buildCreatePayload = () => ({
  cup_type: createForm.cup_type,
  name: createForm.name.trim(),
  portal_title: createForm.portal_title.trim() || createForm.name.trim(),
  planned_topic_count: Number(createForm.planned_topic_count || 0),
  signup_start_at: createForm.signup_start_at || null,
  signup_end_at: createForm.signup_end_at || null,
  topic_open_at: createForm.topic_open_at || null,
  topic_end_at: createForm.topic_end_at || null,
  cycle_start_at: createForm.cycle_start_at || null,
  cycle_end_at: createForm.cycle_end_at || null,
})

const buildUpdatePayload = () => ({
  name: detailForm.name.trim(),
  portal_title: detailForm.portal_title.trim() || detailForm.name.trim(),
  planned_topic_count: Number(detailForm.planned_topic_count || 0),
  signup_start_at: detailForm.signup_start_at || null,
  signup_end_at: detailForm.signup_end_at || null,
  topic_open_at: detailForm.topic_open_at || null,
  topic_end_at: detailForm.topic_end_at || null,
  cycle_start_at: detailForm.cycle_start_at || null,
  cycle_end_at: detailForm.cycle_end_at || null,
})

const fetchDashboard = async () => {
  loading.value = true
  try {
    const [wirelessRes, telecomRes, currentRes] = await Promise.all([
      getCompetitionEvents('wireless'),
      getCompetitionEvents('telecom'),
      getCurrentCompetitionEvent(),
    ])

    const wirelessEvents = Array.isArray(wirelessRes.data) ? wirelessRes.data : []
    const telecomEvents = Array.isArray(telecomRes.data) ? telecomRes.data : []
    events.value = sortEvents([...wirelessEvents, ...telecomEvents])
    currentEvent.value = currentRes.data || null

    if (selectedEvent.value) {
      const stillExists = events.value.some((item) => item.id === selectedEvent.value.id)
      if (stillExists) {
        await loadEventDetail(selectedEvent.value.id, { showError: false, resetTopic: false })
      } else {
        selectedEvent.value = null
      }
    }
  } catch (error) {
    ElMessage.error(getErrorMessage(error, '获取赛事列表失败'))
  } finally {
    loading.value = false
  }
}

const loadEventDetail = async (eventId, options = {}) => {
  const { showError = true, resetTopic = true } = options
  if (!eventId) return

  detailLoading.value = true
  try {
    const res = await getCompetitionEventDetail(eventId)
    selectedEvent.value = res.data || null
    syncDetailForm(selectedEvent.value)
    if (resetTopic) resetTopicForm()
  } catch (error) {
    if (showError) {
      ElMessage.error(getErrorMessage(error, '获取比赛详情失败'))
    }
  } finally {
    detailLoading.value = false
  }
}

const selectEvent = async (event) => {
  if (!event?.id) return
  await loadEventDetail(event.id)
}

const openCreateDialog = () => {
  resetCreateForm()
  createDialogVisible.value = true
}

const submitCreate = async () => {
  if (!validateEventForm(createForm)) return

  creating.value = true
  try {
    const res = await createCompetitionEvent(buildCreatePayload())
    const createdId = res.data?.event_id
    ElMessage.success(res.msg || '比赛创建成功')
    createDialogVisible.value = false
    resetCreateForm()
    await fetchDashboard()
    if (createdId) await loadEventDetail(createdId)
  } catch (error) {
    ElMessage.error(getErrorMessage(error, '创建比赛失败'))
  } finally {
    creating.value = false
  }
}

const saveEventDetails = async () => {
  if (!selectedEvent.value?.id) return
  if (!validateEventForm(detailForm)) return

  savingDetails.value = true
  try {
    const res = await updateCompetitionEvent(selectedEvent.value.id, buildUpdatePayload())
    selectedEvent.value = res.data || selectedEvent.value
    syncDetailForm(selectedEvent.value)
    ElMessage.success(res.msg || '比赛信息已保存')
    await fetchDashboard()
  } catch (error) {
    ElMessage.error(getErrorMessage(error, '保存比赛信息失败'))
  } finally {
    savingDetails.value = false
  }
}

const toggleEventCurrent = async (event) => {
  if (!event?.id) return

  activeSavingId.value = event.id
  try {
    await updateCompetitionActiveState(event.id, !event.is_current)
    ElMessage.success('比赛状态已更新')
    await fetchDashboard()
  } catch (error) {
    ElMessage.error(getErrorMessage(error, '更新比赛状态失败'))
  } finally {
    activeSavingId.value = null
  }
}

const toggleSignupOpen = async (event) => {
  if (!event?.id) return

  signupOpenSavingId.value = event.id
  try {
    await updateCompetitionSignupOpenState(event.id, !event.signup_open)
    ElMessage.success(event.signup_open ? '报名页面已关闭' : '报名页面已开放')
    await fetchDashboard()
  } catch (error) {
    ElMessage.error(getErrorMessage(error, '更新报名页面状态失败'))
  } finally {
    signupOpenSavingId.value = null
  }
}

const goTeamsCenter = async (event) => {
  if (!event?.module_key) return

  await router.push({
    path: '/teams-center',
    query: {
      module_key: event.module_key,
      event_id: event.id,
      event_name: event.display_title || event.portal_title || event.name,
      cup_type: event.cup_type,
    },
  })
}

const selectTopicForEdit = (topic) => {
  selectedTopicId.value = topic.id
  topicForm.title = topic.title || ''
  topicForm.description = topic.description || ''
  topicFile.value = null
  topicUploadList.value = []
}

const resetTopicForm = () => {
  selectedTopicId.value = null
  topicForm.title = ''
  topicForm.description = ''
  topicFile.value = null
  topicUploadList.value = []
}

const isAllowedTopicFile = (file) => /\.(pdf|doc|docx)$/i.test(file?.name || '')

const handleFileChange = (file) => {
  if (!isAllowedTopicFile(file)) {
    ElMessage.warning('仅支持 pdf、doc、docx 文件')
    topicFile.value = null
    topicUploadList.value = []
    return false
  }

  topicFile.value = file.raw
  topicUploadList.value = [file]
  return true
}

const handleFileExceed = (files) => {
  const rawFile = files?.[0]
  if (!isAllowedTopicFile(rawFile)) {
    ElMessage.warning('仅支持 pdf、doc、docx 文件')
    return
  }

  topicFile.value = rawFile
  topicUploadList.value = [{ name: rawFile.name, raw: rawFile }]
}

const handleFileRemove = () => {
  topicFile.value = null
  topicUploadList.value = []
}

const submitTopic = async () => {
  if (!selectedEvent.value?.id) {
    ElMessage.warning('请先选择比赛')
    return
  }
  if (!topicForm.title.trim()) {
    ElMessage.warning('请输入选题名称')
    return
  }

  savingTopic.value = true
  try {
    const payload = {
      title: topicForm.title.trim(),
      description: topicForm.description.trim(),
      document: topicFile.value,
    }

    if (selectedTopicId.value) {
      await updateCompetitionTopic(selectedEvent.value.id, selectedTopicId.value, payload)
      ElMessage.success('选题已保存')
    } else {
      await createCompetitionTopic(selectedEvent.value.id, payload)
      ElMessage.success('选题已添加')
    }

    await loadEventDetail(selectedEvent.value.id, { showError: false })
    await fetchDashboard()
  } catch (error) {
    ElMessage.error(getErrorMessage(error, '保存选题失败'))
  } finally {
    savingTopic.value = false
  }
}

const downloadTopicDocument = (topic) => {
  if (!topic?.document_url) {
    ElMessage.warning('该选题暂无文档')
    return
  }
  window.open(topic.document_url, '_blank')
}

onMounted(fetchDashboard)
</script>

<style scoped>
.event-management-page {
  min-height: 100%;
  overflow-x: hidden;
}

.event-card,
.topic-row {
  min-width: 0;
  transition: border-color 0.2s ease, background-color 0.2s ease, box-shadow 0.2s ease;
}

.event-card:hover,
.topic-row:hover {
  box-shadow: 0 12px 26px -28px rgba(15, 23, 42, 0.45);
}

.event-card:focus-visible,
.topic-row:focus-visible {
  outline: 2px solid #93c5fd;
  outline-offset: 2px;
}

.form-grid :deep(.el-form-item) {
  display: flex;
  flex-direction: column;
  margin-bottom: 0;
  min-width: 0;
}

.form-grid :deep(.el-form-item__label) {
  display: block;
  min-height: 24px;
  margin: 0 0 8px;
  padding: 0 !important;
  line-height: 1.4 !important;
  position: relative;
  z-index: 1;
}

.form-grid :deep(.el-form-item__content) {
  display: flex;
  min-height: 46px;
  min-width: 0;
  width: 100%;
  align-items: center;
  line-height: normal;
}

.event-form-stack {
  display: flex;
  flex-direction: column;
  gap: 28px;
}

.time-pair-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: 28px 18px;
  align-items: start;
}

.event-info-panel {
  padding-bottom: 22px;
}

.topic-section {
  clear: both;
  margin-top: 32px;
}

.topic-editor-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.event-management-page :deep(.el-dialog) {
  max-width: calc(100vw - 24px);
}

.event-management-page :deep(.el-input-number) {
  width: 100%;
}

.event-management-page :deep(.el-input-number .el-input__inner) {
  text-align: left;
}

.topic-upload {
  width: 100%;
}

.topic-upload :deep(.el-upload),
.topic-upload :deep(.el-upload-dragger) {
  width: 100%;
}

.topic-upload :deep(.el-upload-dragger) {
  border-radius: 14px;
  padding: 18px 12px;
}

@media (min-width: 768px) {
  .time-pair-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 640px) {
  .event-management-page :deep(.el-dialog__body) {
    max-height: calc(100vh - 190px);
    overflow-y: auto;
  }
}
</style>
