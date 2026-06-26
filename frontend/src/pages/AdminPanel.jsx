import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import Alert from "../components/Alert.jsx";
import LoadingPanel from "../components/LoadingPanel.jsx";
import PageHeader from "../components/PageHeader.jsx";
import StatCard from "../components/StatCard.jsx";
import { useLanguage } from "../i18n/LanguageContext.jsx";
import { api, apiErrorMessage } from "../services/api";
import { roles, taskCategories, taskDifficulties } from "../services/constants";

const blankUser = { email: "", full_name: "", password: "", role: "student", team_id: "" };
const blankTask = {
  title: "",
  description: "",
  category: "Programming",
  difficulty: "Beginner",
  estimated_hours: 1,
  deadline: "",
  points: 100,
  is_required: true,
  attachments: ""
};
const blankAnnouncement = { title: "", body: "", is_pinned: false, scheduled_for: "", expires_at: "" };
const blankPointAward = { user_id: "", amount: 20, description: "" };
const blankBadgeAward = { user_id: "", badge_code: "" };

export default function AdminPanel() {
  const { formatDateTime, t } = useLanguage();
  const [users, setUsers] = useState([]);
  const [teams, setTeams] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [submissions, setSubmissions] = useState([]);
  const [announcements, setAnnouncements] = useState([]);
  const [badges, setBadges] = useState([]);
  const [statistics, setStatistics] = useState(null);
  const [userForm, setUserForm] = useState(blankUser);
  const [taskForm, setTaskForm] = useState(blankTask);
  const [announcementForm, setAnnouncementForm] = useState(blankAnnouncement);
  const [teamForm, setTeamForm] = useState({ name: "", description: "" });
  const [pointAward, setPointAward] = useState(blankPointAward);
  const [badgeAward, setBadgeAward] = useState(blankBadgeAward);
  const [message, setMessage] = useState(null);
  const [taskError, setTaskError] = useState("");
  const [busyAction, setBusyAction] = useState("");
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState("");
  const [activeSection, setActiveSection] = useState("users");
  const [userSearch, setUserSearch] = useState("");
  const [resetPasswords, setResetPasswords] = useState({});

  useEffect(() => {
    load();
  }, []);

  function load() {
    setLoading(true);
    setLoadError("");
    Promise.all([
      api.get("/users"),
      api.get("/teams"),
      api.get("/tasks"),
      api.get("/submissions"),
      api.get("/announcements"),
      api.get("/badges"),
      api.get("/statistics/overview")
    ])
      .then(([usersResponse, teamsResponse, tasksResponse, submissionsResponse, announcementsResponse, badgesResponse, statisticsResponse]) => {
        setUsers(usersResponse.data);
        setTeams(teamsResponse.data);
        setTasks(tasksResponse.data);
        setSubmissions(submissionsResponse.data);
        setAnnouncements(announcementsResponse.data);
        setBadges(badgesResponse.data);
        setStatistics(statisticsResponse.data);
      })
      .catch((err) => {
        const text = apiErrorMessage(err);
        setLoadError(text);
        showMessage("error", text);
      })
      .finally(() => setLoading(false));
  }

  function showMessage(type, text) {
    setMessage({ type, text });
  }

  async function createUser(event) {
    event.preventDefault();
    setMessage(null);
    setBusyAction("create-user");
    try {
      await api.post("/users", { ...userForm, team_id: userForm.team_id ? Number(userForm.team_id) : null });
      setUserForm(blankUser);
      showMessage("success", t("userCreated"));
      load();
    } catch (err) {
      showMessage("error", apiErrorMessage(err));
    } finally {
      setBusyAction("");
    }
  }

  async function createTask(event) {
    event.preventDefault();
    setTaskError("");
    setMessage(null);
    const validationError = validateTaskForm(taskForm, t);
    if (validationError) {
      setTaskError(validationError);
      showMessage("error", validationError);
      return;
    }
    setBusyAction("task");
    try {
      await api.post("/tasks", {
        ...taskForm,
        estimated_hours: Number(taskForm.estimated_hours),
        points: Number(taskForm.points),
        deadline: new Date(taskForm.deadline).toISOString(),
        attachments: parseAttachmentLines(taskForm.attachments)
      });
      setTaskForm(blankTask);
      showMessage("success", t("taskCreated"));
      load();
    } catch (err) {
      const text = apiErrorMessage(err);
      setTaskError(text);
      showMessage("error", text);
    } finally {
      setBusyAction("");
    }
  }

  async function createAnnouncement(event) {
    event.preventDefault();
    setBusyAction("create-announcement");
    try {
      await api.post("/announcements", {
        ...announcementForm,
        scheduled_for: announcementForm.scheduled_for ? new Date(announcementForm.scheduled_for).toISOString() : null,
        expires_at: announcementForm.expires_at ? new Date(announcementForm.expires_at).toISOString() : null
      });
      setAnnouncementForm(blankAnnouncement);
      showMessage("success", t("announcementPublished"));
      load();
    } catch (err) {
      showMessage("error", apiErrorMessage(err));
    } finally {
      setBusyAction("");
    }
  }

  async function createTeam(event) {
    event.preventDefault();
    setBusyAction("create-team");
    try {
      await api.post("/teams", teamForm);
      setTeamForm({ name: "", description: "" });
      showMessage("success", t("teamCreated"));
      load();
    } catch (err) {
      showMessage("error", apiErrorMessage(err));
    } finally {
      setBusyAction("");
    }
  }

  async function promote(teamId, userId) {
    setBusyAction(`promote-${teamId}`);
    try {
      await api.post(`/teams/${teamId}/leader/${userId}`);
      showMessage("success", t("teamLeaderPromoted"));
      load();
    } catch (err) {
      showMessage("error", apiErrorMessage(err));
    } finally {
      setBusyAction("");
    }
  }

  async function saveUser(user) {
    setBusyAction(`user-${user.id}`);
    try {
      const password = resetPasswords[user.id]?.trim();
      const payload = {
        full_name: user.full_name,
        role: user.role,
        team_id: user.team_id || null,
        is_active: user.is_active
      };
      if (password) {
        payload.password = password;
      }
      await api.patch(`/users/${user.id}`, payload);
      setResetPasswords((current) => ({ ...current, [user.id]: "" }));
      showMessage("success", t("userUpdated"));
      load();
    } catch (err) {
      showMessage("error", apiErrorMessage(err));
    } finally {
      setBusyAction("");
    }
  }

  async function deleteTask(taskId) {
    setBusyAction(`delete-task-${taskId}`);
    try {
      await api.delete(`/tasks/${taskId}`);
      showMessage("success", t("taskDeleted"));
      load();
    } catch (err) {
      showMessage("error", apiErrorMessage(err));
    } finally {
      setBusyAction("");
    }
  }

  async function saveTask(task) {
    setBusyAction(`task-${task.id}`);
    try {
      await api.patch(`/tasks/${task.id}`, {
        title: task.title,
        points: Number(task.points),
        deadline: new Date(task.deadline).toISOString(),
        is_required: task.is_required
      });
      showMessage("success", t("taskUpdated"));
      load();
    } catch (err) {
      showMessage("error", apiErrorMessage(err));
    } finally {
      setBusyAction("");
    }
  }

  async function saveTeam(team) {
    setBusyAction(`team-${team.id}`);
    try {
      await api.patch(`/teams/${team.id}`, {
        name: team.name,
        description: team.description || ""
      });
      showMessage("success", t("teamUpdated"));
      load();
    } catch (err) {
      showMessage("error", apiErrorMessage(err));
    } finally {
      setBusyAction("");
    }
  }

  async function saveAnnouncement(announcement) {
    setBusyAction(`announcement-${announcement.id}`);
    try {
      await api.patch(`/announcements/${announcement.id}`, {
        title: announcement.title,
        body: announcement.body,
        is_pinned: announcement.is_pinned
      });
      showMessage("success", t("announcementUpdated"));
      load();
    } catch (err) {
      showMessage("error", apiErrorMessage(err));
    } finally {
      setBusyAction("");
    }
  }

  async function toggleAnnouncement(announcement) {
    setBusyAction(`pin-announcement-${announcement.id}`);
    try {
      await api.patch(`/announcements/${announcement.id}`, { is_pinned: !announcement.is_pinned });
      showMessage("success", t("announcementUpdated"));
      load();
    } catch (err) {
      showMessage("error", apiErrorMessage(err));
    } finally {
      setBusyAction("");
    }
  }

  async function deleteAnnouncement(announcementId) {
    setBusyAction(`delete-announcement-${announcementId}`);
    try {
      await api.delete(`/announcements/${announcementId}`);
      showMessage("success", t("announcementDeleted"));
      load();
    } catch (err) {
      showMessage("error", apiErrorMessage(err));
    } finally {
      setBusyAction("");
    }
  }

  async function awardPoints(event) {
    event.preventDefault();
    setBusyAction("award-points");
    try {
      await api.post(`/users/${pointAward.user_id}/points`, {
        amount: Number(pointAward.amount),
        description: pointAward.description || "Administrative points adjustment"
      });
      setPointAward(blankPointAward);
      showMessage("success", t("pointsAwarded"));
      load();
    } catch (err) {
      showMessage("error", apiErrorMessage(err));
    } finally {
      setBusyAction("");
    }
  }

  async function awardBadge(event) {
    event.preventDefault();
    setBusyAction("award-badge");
    try {
      await api.post("/badges/award", {
        user_id: Number(badgeAward.user_id),
        badge_code: badgeAward.badge_code
      });
      setBadgeAward(blankBadgeAward);
      showMessage("success", t("badgeAwarded"));
      load();
    } catch (err) {
      showMessage("error", apiErrorMessage(err));
    } finally {
      setBusyAction("");
    }
  }

  const normalizedSearch = userSearch.trim().toLowerCase();
  const displayedUsers = normalizedSearch
    ? users.filter((user) => {
      const teamName = teams.find((team) => team.id === user.team_id)?.name || "";
      return [user.full_name, user.email, user.role, teamName].join(" ").toLowerCase().includes(normalizedSearch);
    })
    : users;

  return (
    <>
      <PageHeader title={t("adminTitle")} eyebrow={t("adminEyebrow")} />
      <Toast message={message} onClose={() => setMessage(null)} />
      {loadError && <Alert tone="error" className="mb-4">{loadError}</Alert>}
      {loading && <LoadingPanel label={t("loadingAdmin")} />}

      {!loading && statistics && (
        <section className="mb-6 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <StatCard label={t("totalMembers")} value={statistics.total_members} />
          <StatCard label={t("activeMembers")} value={statistics.active_members} detail={t("submittedLast7Days")} />
          <StatCard label={t("completedTasks")} value={statistics.completed_tasks} />
          <StatCard label={t("submissionRate")} value={`${statistics.submission_rate}%`} />
        </section>
      )}

      {!loading && !loadError && (
      <>
      <div className="mb-6 flex gap-2 overflow-x-auto rounded-lg border border-slate-200 bg-white p-1 dark:border-slate-800 dark:bg-slate-900">
        {[
          ["users", t("users")],
          ["teams", t("teams")],
          ["tasks", t("tasks")],
          ["announcements", t("announcements")],
          ["submissions", t("adminSubmissions")],
          ["statistics", t("statistics")]
        ].map(([key, label]) => (
          <button
            key={key}
            className={`shrink-0 rounded-md px-4 py-2 text-sm font-semibold transition ${activeSection === key ? "bg-teal-700 text-white dark:bg-teal-500 dark:text-slate-950" : "text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800"}`}
            type="button"
            onClick={() => setActiveSection(key)}
          >
            {label}
          </button>
        ))}
      </div>

      <section className="grid gap-6 xl:grid-cols-2">
        {activeSection === "users" && <AdminForm title={t("createUser")} onSubmit={createUser} busy={busyAction === "create-user"}>
          <input className="input" placeholder={t("fullName")} value={userForm.full_name} onChange={(event) => setUserForm({ ...userForm, full_name: event.target.value })} required />
          <input className="input" placeholder={t("email")} type="email" value={userForm.email} onChange={(event) => setUserForm({ ...userForm, email: event.target.value })} required />
          <input className="input" placeholder={t("password")} type="password" value={userForm.password} onChange={(event) => setUserForm({ ...userForm, password: event.target.value })} required minLength={8} maxLength={72} />
          <div className="grid gap-3 sm:grid-cols-2">
            <select className="input" value={userForm.role} onChange={(event) => setUserForm({ ...userForm, role: event.target.value })}>
              {roles.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
            </select>
            <select className="input" value={userForm.team_id} onChange={(event) => setUserForm({ ...userForm, team_id: event.target.value })}>
              <option value="">{t("noTeam")}</option>
              {teams.map((team) => <option key={team.id} value={team.id}>{team.name}</option>)}
            </select>
          </div>
        </AdminForm>}

        {activeSection === "teams" && <AdminForm title={t("createTeam")} onSubmit={createTeam} busy={busyAction === "create-team"}>
          <input className="input" placeholder={t("teamName")} value={teamForm.name} onChange={(event) => setTeamForm({ ...teamForm, name: event.target.value })} required />
          <textarea className="input min-h-28" placeholder={t("description")} value={teamForm.description} onChange={(event) => setTeamForm({ ...teamForm, description: event.target.value })} />
        </AdminForm>}

        {activeSection === "tasks" && <AdminForm title={t("createTask")} onSubmit={createTask} feedback={taskError} busy={busyAction === "task"}>
          <input className="input" placeholder={t("title")} value={taskForm.title} onChange={(event) => setTaskForm({ ...taskForm, title: event.target.value })} required />
          <textarea className="input min-h-28" placeholder={t("description")} value={taskForm.description} onChange={(event) => setTaskForm({ ...taskForm, description: event.target.value })} required />
          <div className="grid gap-3 sm:grid-cols-2">
            <select className="input" value={taskForm.category} onChange={(event) => setTaskForm({ ...taskForm, category: event.target.value })}>
              {taskCategories.map((item) => <option key={item}>{item}</option>)}
            </select>
            <select className="input" value={taskForm.difficulty} onChange={(event) => setTaskForm({ ...taskForm, difficulty: event.target.value })}>
              {taskDifficulties.map((item) => <option key={item}>{item}</option>)}
            </select>
          </div>
          <div className="grid gap-3 sm:grid-cols-3">
            <input className="input" type="number" min="1" value={taskForm.estimated_hours} onChange={(event) => setTaskForm({ ...taskForm, estimated_hours: event.target.value })} />
            <input className="input" type="number" min="1" value={taskForm.points} onChange={(event) => setTaskForm({ ...taskForm, points: event.target.value })} />
            <input className="input" type="datetime-local" value={taskForm.deadline} onChange={(event) => setTaskForm({ ...taskForm, deadline: event.target.value })} required />
          </div>
          <label className="flex items-center gap-2 text-sm">
            <input type="checkbox" checked={taskForm.is_required} onChange={(event) => setTaskForm({ ...taskForm, is_required: event.target.checked })} />
            {t("requiredTask")}
          </label>
          <textarea className="input min-h-20" placeholder={t("attachmentUrls")} value={taskForm.attachments} onChange={(event) => setTaskForm({ ...taskForm, attachments: event.target.value })} />
        </AdminForm>}

        {activeSection === "announcements" && <AdminForm title={t("createAnnouncement")} onSubmit={createAnnouncement} busy={busyAction === "create-announcement"}>
          <input className="input" placeholder={t("title")} value={announcementForm.title} onChange={(event) => setAnnouncementForm({ ...announcementForm, title: event.target.value })} required />
          <textarea className="input min-h-32" placeholder={t("description")} value={announcementForm.body} onChange={(event) => setAnnouncementForm({ ...announcementForm, body: event.target.value })} required />
          <label className="flex items-center gap-2 text-sm">
            <input type="checkbox" checked={announcementForm.is_pinned} onChange={(event) => setAnnouncementForm({ ...announcementForm, is_pinned: event.target.checked })} />
            {t("pin")}
          </label>
          <div className="grid gap-3 sm:grid-cols-2">
            <input className="input" type="datetime-local" value={announcementForm.scheduled_for} onChange={(event) => setAnnouncementForm({ ...announcementForm, scheduled_for: event.target.value })} />
            <input className="input" type="datetime-local" value={announcementForm.expires_at} onChange={(event) => setAnnouncementForm({ ...announcementForm, expires_at: event.target.value })} />
          </div>
        </AdminForm>}

        {activeSection === "users" && <AdminForm title={t("awardPoints")} onSubmit={awardPoints} busy={busyAction === "award-points"}>
          <select className="input" value={pointAward.user_id} onChange={(event) => setPointAward({ ...pointAward, user_id: event.target.value })} required>
            <option value="">{t("chooseMember")}</option>
            {users.map((user) => <option key={user.id} value={user.id}>{user.full_name}</option>)}
          </select>
          <input className="input" type="number" min="-10000" max="10000" value={pointAward.amount} onChange={(event) => setPointAward({ ...pointAward, amount: event.target.value })} required />
          <input className="input" placeholder={t("reason")} value={pointAward.description} onChange={(event) => setPointAward({ ...pointAward, description: event.target.value })} />
        </AdminForm>}

        {activeSection === "users" && <AdminForm title={t("awardBadge")} onSubmit={awardBadge} busy={busyAction === "award-badge"}>
          <select className="input" value={badgeAward.user_id} onChange={(event) => setBadgeAward({ ...badgeAward, user_id: event.target.value })} required>
            <option value="">{t("chooseMember")}</option>
            {users.map((user) => <option key={user.id} value={user.id}>{user.full_name}</option>)}
          </select>
          <select className="input" value={badgeAward.badge_code} onChange={(event) => setBadgeAward({ ...badgeAward, badge_code: event.target.value })} required>
            <option value="">{t("chooseBadge")}</option>
            {badges.map((badge) => <option key={badge.id} value={badge.code}>{badge.name}</option>)}
          </select>
        </AdminForm>}
      </section>

      <section className="mt-6 grid gap-6 xl:grid-cols-2">
        {activeSection === "users" && <div className="panel p-5 xl:col-span-2">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <h2 className="font-bold">{t("users")}</h2>
            <input
              className="input sm:max-w-sm"
              placeholder={t("searchUsers")}
              value={userSearch}
              onChange={(event) => setUserSearch(event.target.value)}
            />
          </div>
          <div className="mt-4 overflow-x-auto">
            <table className="min-w-full divide-y divide-slate-200 text-sm dark:divide-slate-800">
              <thead>
                <tr>
                  {[t("name"), t("role"), t("team"), t("active"), t("resetPassword"), t("action")].map((heading) => (
                    <th key={heading} className="px-3 py-2 text-left font-semibold">{heading}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200 dark:divide-slate-800">
                {displayedUsers.map((user) => (
                  <tr key={user.id}>
                    <td className="px-3 py-2">
                      <input
                        className="input min-w-48"
                        value={user.full_name}
                        onChange={(event) => setUsers(users.map((item) => item.id === user.id ? { ...item, full_name: event.target.value } : item))}
                      />
                    </td>
                    <td className="px-3 py-2">
                      <select className="input min-w-36" value={user.role} onChange={(event) => setUsers(users.map((item) => item.id === user.id ? { ...item, role: event.target.value } : item))}>
                        {roles.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
                      </select>
                    </td>
                    <td className="px-3 py-2">
                      <select className="input min-w-44" value={user.team_id || ""} onChange={(event) => setUsers(users.map((item) => item.id === user.id ? { ...item, team_id: event.target.value ? Number(event.target.value) : null } : item))}>
                        <option value="">{t("noTeam")}</option>
                        {teams.map((team) => <option key={team.id} value={team.id}>{team.name}</option>)}
                      </select>
                    </td>
                    <td className="px-3 py-2">
                      <input type="checkbox" checked={user.is_active} onChange={(event) => setUsers(users.map((item) => item.id === user.id ? { ...item, is_active: event.target.checked } : item))} />
                    </td>
                    <td className="px-3 py-2">
                      <input
                        className="input min-w-56"
                        placeholder={t("leaveBlank")}
                        type="password"
                        value={resetPasswords[user.id] || ""}
                        onChange={(event) => setResetPasswords((current) => ({ ...current, [user.id]: event.target.value }))}
                        minLength={8}
                        maxLength={72}
                      />
                    </td>
                    <td className="px-3 py-2">
                      <button className="btn-secondary disabled:cursor-not-allowed disabled:opacity-60" type="button" disabled={busyAction === `user-${user.id}`} onClick={() => saveUser(user)}>
                        {busyAction === `user-${user.id}` ? t("savingEllipsis") : t("save")}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {displayedUsers.length === 0 && <p className="p-4 text-sm text-slate-500">{t("noUsers")}</p>}
          </div>
        </div>}

        {activeSection === "teams" && <div className="panel p-5 xl:col-span-2">
          <h2 className="font-bold">{t("teams")}</h2>
          <div className="mt-4 space-y-3">
            {teams.map((team) => (
              <div key={team.id} className="rounded-lg bg-slate-50 p-4 dark:bg-slate-800">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div>
                    <input className="input font-semibold" value={team.name} onChange={(event) => setTeams(teams.map((item) => item.id === team.id ? { ...item, name: event.target.value } : item))} />
                    <p className="text-sm text-slate-500">{team.member_count} {t("members")}</p>
                  </div>
                  <div className="grid w-full gap-2 sm:w-auto sm:min-w-56">
                    <select className="input" defaultValue="" disabled={busyAction === `promote-${team.id}`} onChange={(event) => event.target.value && promote(team.id, event.target.value)}>
                      <option value="">{t("promoteLeader")}</option>
                      {users.map((user) => <option key={user.id} value={user.id}>{user.full_name}</option>)}
                    </select>
                    <button className="btn-secondary disabled:cursor-not-allowed disabled:opacity-60" type="button" disabled={busyAction === `team-${team.id}`} onClick={() => saveTeam(team)}>
                      {busyAction === `team-${team.id}` ? t("savingEllipsis") : t("saveTeam")}
                    </button>
                  </div>
                </div>
                <textarea className="input mt-3 min-h-20" value={team.description || ""} onChange={(event) => setTeams(teams.map((item) => item.id === team.id ? { ...item, description: event.target.value } : item))} />
              </div>
            ))}
            {teams.length === 0 && <p className="text-sm text-slate-500">{t("noTeams")}</p>}
          </div>
        </div>}
        {activeSection === "tasks" && <div className="panel p-5 xl:col-span-2">
          <h2 className="font-bold">{t("tasks")}</h2>
          <div className="mt-4 space-y-3">
            {tasks.map((task) => (
              <div key={task.id} className="rounded-lg bg-slate-50 p-4 dark:bg-slate-800">
                <div className="grid gap-3 lg:grid-cols-[1fr_110px_190px_auto] lg:items-center">
                  <input className="input" value={task.title} onChange={(event) => setTasks(tasks.map((item) => item.id === task.id ? { ...item, title: event.target.value } : item))} />
                  <input className="input" type="number" min="1" value={task.points} onChange={(event) => setTasks(tasks.map((item) => item.id === task.id ? { ...item, points: event.target.value } : item))} />
                  <input className="input" type="datetime-local" value={toDateTimeLocal(task.deadline)} onChange={(event) => setTasks(tasks.map((item) => item.id === task.id ? { ...item, deadline: event.target.value } : item))} />
                  <div className="flex gap-2">
                    <button className="btn-secondary disabled:cursor-not-allowed disabled:opacity-60" type="button" disabled={busyAction === `task-${task.id}`} onClick={() => saveTask(task)}>
                      {busyAction === `task-${task.id}` ? t("savingEllipsis") : t("save")}
                    </button>
                    <button className="btn-secondary disabled:cursor-not-allowed disabled:opacity-60" type="button" disabled={busyAction === `delete-task-${task.id}`} onClick={() => deleteTask(task.id)}>
                      {busyAction === `delete-task-${task.id}` ? t("deleting") : t("delete")}
                    </button>
                  </div>
                </div>
                <label className="mt-3 flex items-center gap-2 text-sm">
                  <input type="checkbox" checked={task.is_required} onChange={(event) => setTasks(tasks.map((item) => item.id === task.id ? { ...item, is_required: event.target.checked } : item))} />
                  {t("requiredTask")} · {task.category}
                </label>
              </div>
            ))}
            {tasks.length === 0 && <p className="text-sm text-slate-500">{t("noTasksYet")}</p>}
          </div>
        </div>}
        {activeSection === "announcements" && <div className="panel p-5 xl:col-span-2">
          <h2 className="font-bold">{t("announcements")}</h2>
          <div className="mt-4 space-y-3">
            {announcements.map((announcement) => (
              <div key={announcement.id} className="rounded-lg bg-slate-50 p-4 dark:bg-slate-800">
                <input className="input" value={announcement.title} onChange={(event) => setAnnouncements(announcements.map((item) => item.id === announcement.id ? { ...item, title: event.target.value } : item))} />
                <textarea className="input mt-3 min-h-20" value={announcement.body} onChange={(event) => setAnnouncements(announcements.map((item) => item.id === announcement.id ? { ...item, body: event.target.value } : item))} />
                <div className="mt-3 flex flex-wrap gap-2">
                  <button className="btn-secondary disabled:cursor-not-allowed disabled:opacity-60" type="button" disabled={busyAction === `announcement-${announcement.id}`} onClick={() => saveAnnouncement(announcement)}>
                    {busyAction === `announcement-${announcement.id}` ? t("savingEllipsis") : t("save")}
                  </button>
                  <button className="btn-secondary disabled:cursor-not-allowed disabled:opacity-60" type="button" disabled={busyAction === `pin-announcement-${announcement.id}`} onClick={() => toggleAnnouncement(announcement)}>{announcement.is_pinned ? t("unpin") : t("pin")}</button>
                  <button className="btn-secondary disabled:cursor-not-allowed disabled:opacity-60" type="button" disabled={busyAction === `delete-announcement-${announcement.id}`} onClick={() => deleteAnnouncement(announcement.id)}>
                    {busyAction === `delete-announcement-${announcement.id}` ? t("deleting") : t("delete")}
                  </button>
                </div>
              </div>
            ))}
            {announcements.length === 0 && <p className="text-sm text-slate-500">{t("noAnnouncementsYet")}</p>}
          </div>
        </div>}
        {activeSection === "submissions" && <div className="panel p-5 xl:col-span-2">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <h2 className="font-bold">{t("adminSubmissions")}</h2>
            <Link className="btn-secondary" to="/submissions">{t("openSubmissionsReview")}</Link>
          </div>
          <div className="mt-4 overflow-x-auto">
            <table className="min-w-full divide-y divide-slate-200 text-sm dark:divide-slate-800">
              <thead>
                <tr>
                  {[t("tasks"), t("student"), t("team"), t("status"), t("submitted"), t("proof")].map((heading) => (
                    <th key={heading} className="px-3 py-2 text-left font-semibold">{heading}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200 dark:divide-slate-800">
                {submissions.map((item) => (
                  <tr key={item.id}>
                    <td className="px-3 py-2 font-semibold">{item.task_title}</td>
                    <td className="px-3 py-2">{item.student_name}</td>
                    <td className="px-3 py-2">{item.team_name || t("noTeam")}</td>
                    <td className="px-3 py-2">{item.status}</td>
                    <td className="px-3 py-2">{formatDateTime(item.submitted_at)}</td>
                    <td className="px-3 py-2">{[item.link_url && t("link"), item.github_url && "GitHub", item.file_url && t("file")].filter(Boolean).join(" · ") || "-"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            {submissions.length === 0 && <p className="p-4 text-sm text-slate-500">{t("noSubmissionsYet")}</p>}
          </div>
        </div>}
        {activeSection === "statistics" && <div className="panel p-5 xl:col-span-2">
          <h2 className="font-bold">{t("topMembers")}</h2>
          <div className="mt-4 space-y-3">
            {statistics?.top_members?.map((member) => (
              <div key={member.id} className="flex items-center justify-between rounded-lg bg-slate-50 p-4 dark:bg-slate-800">
                <p className="font-semibold">{member.full_name}</p>
                <p className="font-bold text-teal-700 dark:text-teal-300">{member.points} pts</p>
              </div>
            ))}
          </div>
        </div>}
      </section>
      </>
      )}
    </>
  );
}

function AdminForm({ title, children, onSubmit, feedback = "", busy = false }) {
  const { t } = useLanguage();
  return (
    <form className="panel p-5" onSubmit={onSubmit} noValidate>
      <h2 className="mb-4 font-bold">{title}</h2>
      <div className="space-y-3">{children}</div>
      {feedback && (
        <p className="mt-4 rounded-lg bg-rose-50 px-4 py-3 text-sm font-semibold text-rose-700 dark:bg-rose-500/10 dark:text-rose-200">
          {feedback}
        </p>
      )}
      <button className="btn-primary mt-4 w-full disabled:cursor-not-allowed disabled:opacity-60" disabled={busy}>
        {busy ? t("savingEllipsis") : t("save")}
      </button>
    </form>
  );
}

function Toast({ message, onClose }) {
  const { t } = useLanguage();
  if (!message) {
    return null;
  }
  const isError = message.type === "error";
  return (
    <div className="fixed inset-x-3 top-3 z-50 mx-auto max-w-2xl sm:top-4" role="status" aria-live="polite">
      <div className={`flex items-start justify-between gap-3 rounded-lg border px-4 py-3 text-sm font-semibold shadow-soft ${
        isError
          ? "border-rose-200 bg-rose-50 text-rose-800 dark:border-rose-500/30 dark:bg-rose-500/15 dark:text-rose-100"
          : "border-teal-200 bg-teal-50 text-teal-800 dark:border-teal-500/30 dark:bg-teal-500/15 dark:text-teal-100"
      }`}>
        <span>{message.text}</span>
        <button className="shrink-0 rounded-md px-2 py-1 text-xs opacity-75 hover:opacity-100" type="button" onClick={onClose}>
          {t("close")}
        </button>
      </div>
    </div>
  );
}

function parseAttachmentLines(value) {
  return value.split("\n").map((item) => item.trim()).filter(Boolean);
}

function validateTaskForm(form, t) {
  if (form.title.trim().length < 3) {
    return t("taskTitleRequired");
  }
  if (form.description.trim().length < 10) {
    return t("taskDescriptionRequired");
  }
  if (!form.deadline || Number.isNaN(new Date(form.deadline).getTime())) {
    return t("deadlineRequired");
  }
  if (Number(form.estimated_hours) < 1 || Number(form.estimated_hours) > 500) {
    return t("hoursRange");
  }
  if (Number(form.points) < 1 || Number(form.points) > 10000) {
    return t("pointsRange");
  }
  const invalidAttachment = parseAttachmentLines(form.attachments).find((item) => !item.startsWith("http://") && !item.startsWith("https://"));
  if (invalidAttachment) {
    return t("invalidAttachment");
  }
  return "";
}

function toDateTimeLocal(value) {
  if (!value) {
    return "";
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  const localDate = new Date(date.getTime() - date.getTimezoneOffset() * 60000);
  return localDate.toISOString().slice(0, 16);
}
