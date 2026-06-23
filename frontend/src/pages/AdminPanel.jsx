import { useEffect, useState } from "react";

import PageHeader from "../components/PageHeader.jsx";
import StatCard from "../components/StatCard.jsx";
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

export default function AdminPanel() {
  const [users, setUsers] = useState([]);
  const [teams, setTeams] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [announcements, setAnnouncements] = useState([]);
  const [statistics, setStatistics] = useState(null);
  const [userForm, setUserForm] = useState(blankUser);
  const [taskForm, setTaskForm] = useState(blankTask);
  const [announcementForm, setAnnouncementForm] = useState(blankAnnouncement);
  const [teamForm, setTeamForm] = useState({ name: "", description: "" });
  const [message, setMessage] = useState("");

  useEffect(() => {
    load();
  }, []);

  function load() {
    api.get("/users").then(({ data }) => setUsers(data));
    api.get("/teams").then(({ data }) => setTeams(data));
    api.get("/tasks").then(({ data }) => setTasks(data));
    api.get("/announcements").then(({ data }) => setAnnouncements(data));
    api.get("/statistics/overview").then(({ data }) => setStatistics(data));
  }

  async function createUser(event) {
    event.preventDefault();
    setMessage("");
    try {
      await api.post("/users", { ...userForm, team_id: userForm.team_id ? Number(userForm.team_id) : null });
      setUserForm(blankUser);
      setMessage("User created.");
      load();
    } catch (err) {
      setMessage(apiErrorMessage(err));
    }
  }

  async function createTask(event) {
    event.preventDefault();
    try {
      await api.post("/tasks", {
        ...taskForm,
        estimated_hours: Number(taskForm.estimated_hours),
        points: Number(taskForm.points),
        deadline: new Date(taskForm.deadline).toISOString(),
        attachments: taskForm.attachments.split("\n").map((item) => item.trim()).filter(Boolean)
      });
      setTaskForm(blankTask);
      setMessage("Task created and students notified.");
      load();
    } catch (err) {
      setMessage(apiErrorMessage(err));
    }
  }

  async function createAnnouncement(event) {
    event.preventDefault();
    try {
      await api.post("/announcements", {
        ...announcementForm,
        scheduled_for: announcementForm.scheduled_for ? new Date(announcementForm.scheduled_for).toISOString() : null,
        expires_at: announcementForm.expires_at ? new Date(announcementForm.expires_at).toISOString() : null
      });
      setAnnouncementForm(blankAnnouncement);
      setMessage("Announcement published.");
      load();
    } catch (err) {
      setMessage(apiErrorMessage(err));
    }
  }

  async function createTeam(event) {
    event.preventDefault();
    try {
      await api.post("/teams", teamForm);
      setTeamForm({ name: "", description: "" });
      setMessage("Team created.");
      load();
    } catch (err) {
      setMessage(apiErrorMessage(err));
    }
  }

  async function promote(teamId, userId) {
    try {
      await api.post(`/teams/${teamId}/leader/${userId}`);
      setMessage("Team leader promoted.");
      load();
    } catch (err) {
      setMessage(apiErrorMessage(err));
    }
  }

  async function saveUser(user) {
    try {
      await api.patch(`/users/${user.id}`, {
        full_name: user.full_name,
        role: user.role,
        team_id: user.team_id || null,
        is_active: user.is_active
      });
      setMessage("User updated.");
      load();
    } catch (err) {
      setMessage(apiErrorMessage(err));
    }
  }

  async function deleteTask(taskId) {
    try {
      await api.delete(`/tasks/${taskId}`);
      setMessage("Task deleted.");
      load();
    } catch (err) {
      setMessage(apiErrorMessage(err));
    }
  }

  async function saveTask(task) {
    try {
      await api.patch(`/tasks/${task.id}`, {
        title: task.title,
        points: Number(task.points),
        deadline: new Date(task.deadline).toISOString(),
        is_required: task.is_required
      });
      setMessage("Task updated.");
      load();
    } catch (err) {
      setMessage(apiErrorMessage(err));
    }
  }

  async function saveAnnouncement(announcement) {
    try {
      await api.patch(`/announcements/${announcement.id}`, {
        title: announcement.title,
        body: announcement.body,
        is_pinned: announcement.is_pinned
      });
      setMessage("Announcement updated.");
      load();
    } catch (err) {
      setMessage(apiErrorMessage(err));
    }
  }

  async function toggleAnnouncement(announcement) {
    try {
      await api.patch(`/announcements/${announcement.id}`, { is_pinned: !announcement.is_pinned });
      setMessage("Announcement updated.");
      load();
    } catch (err) {
      setMessage(apiErrorMessage(err));
    }
  }

  async function deleteAnnouncement(announcementId) {
    try {
      await api.delete(`/announcements/${announcementId}`);
      setMessage("Announcement deleted.");
      load();
    } catch (err) {
      setMessage(apiErrorMessage(err));
    }
  }

  return (
    <>
      <PageHeader title="Admin Panel" eyebrow="Users, teams, tasks, announcements, and statistics" />
      {message && <p className="mb-4 rounded-lg bg-slate-100 px-4 py-3 text-sm dark:bg-slate-800">{message}</p>}

      {statistics && (
        <section className="mb-6 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <StatCard label="Total members" value={statistics.total_members} />
          <StatCard label="Active members" value={statistics.active_members} detail="Submitted in last 7 days" />
          <StatCard label="Completed tasks" value={statistics.completed_tasks} />
          <StatCard label="Submission rate" value={`${statistics.submission_rate}%`} />
        </section>
      )}

      <section className="grid gap-6 xl:grid-cols-2">
        <AdminForm title="Create user" onSubmit={createUser}>
          <input className="input" placeholder="Full name" value={userForm.full_name} onChange={(event) => setUserForm({ ...userForm, full_name: event.target.value })} required />
          <input className="input" placeholder="Email" type="email" value={userForm.email} onChange={(event) => setUserForm({ ...userForm, email: event.target.value })} required />
          <input className="input" placeholder="Password" type="password" value={userForm.password} onChange={(event) => setUserForm({ ...userForm, password: event.target.value })} required minLength={8} maxLength={72} />
          <div className="grid gap-3 sm:grid-cols-2">
            <select className="input" value={userForm.role} onChange={(event) => setUserForm({ ...userForm, role: event.target.value })}>
              {roles.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
            </select>
            <select className="input" value={userForm.team_id} onChange={(event) => setUserForm({ ...userForm, team_id: event.target.value })}>
              <option value="">No team</option>
              {teams.map((team) => <option key={team.id} value={team.id}>{team.name}</option>)}
            </select>
          </div>
        </AdminForm>

        <AdminForm title="Create team" onSubmit={createTeam}>
          <input className="input" placeholder="Team name" value={teamForm.name} onChange={(event) => setTeamForm({ ...teamForm, name: event.target.value })} required />
          <textarea className="input min-h-28" placeholder="Description" value={teamForm.description} onChange={(event) => setTeamForm({ ...teamForm, description: event.target.value })} />
        </AdminForm>

        <AdminForm title="Create task" onSubmit={createTask}>
          <input className="input" placeholder="Title" value={taskForm.title} onChange={(event) => setTaskForm({ ...taskForm, title: event.target.value })} required />
          <textarea className="input min-h-28" placeholder="Description" value={taskForm.description} onChange={(event) => setTaskForm({ ...taskForm, description: event.target.value })} required />
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
            Required task
          </label>
          <textarea className="input min-h-20" placeholder="Attachment URLs, one per line" value={taskForm.attachments} onChange={(event) => setTaskForm({ ...taskForm, attachments: event.target.value })} />
        </AdminForm>

        <AdminForm title="Create announcement" onSubmit={createAnnouncement}>
          <input className="input" placeholder="Title" value={announcementForm.title} onChange={(event) => setAnnouncementForm({ ...announcementForm, title: event.target.value })} required />
          <textarea className="input min-h-32" placeholder="Announcement body" value={announcementForm.body} onChange={(event) => setAnnouncementForm({ ...announcementForm, body: event.target.value })} required />
          <label className="flex items-center gap-2 text-sm">
            <input type="checkbox" checked={announcementForm.is_pinned} onChange={(event) => setAnnouncementForm({ ...announcementForm, is_pinned: event.target.checked })} />
            Pin announcement
          </label>
          <div className="grid gap-3 sm:grid-cols-2">
            <input className="input" type="datetime-local" value={announcementForm.scheduled_for} onChange={(event) => setAnnouncementForm({ ...announcementForm, scheduled_for: event.target.value })} />
            <input className="input" type="datetime-local" value={announcementForm.expires_at} onChange={(event) => setAnnouncementForm({ ...announcementForm, expires_at: event.target.value })} />
          </div>
        </AdminForm>
      </section>

      <section className="mt-6 grid gap-6 xl:grid-cols-2">
        <div className="panel p-5 xl:col-span-2">
          <h2 className="font-bold">Manage users</h2>
          <div className="mt-4 overflow-x-auto">
            <table className="min-w-full divide-y divide-slate-200 text-sm dark:divide-slate-800">
              <thead>
                <tr>
                  {["Name", "Role", "Team", "Active", "Action"].map((heading) => (
                    <th key={heading} className="px-3 py-2 text-left font-semibold">{heading}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200 dark:divide-slate-800">
                {users.map((user) => (
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
                        <option value="">No team</option>
                        {teams.map((team) => <option key={team.id} value={team.id}>{team.name}</option>)}
                      </select>
                    </td>
                    <td className="px-3 py-2">
                      <input type="checkbox" checked={user.is_active} onChange={(event) => setUsers(users.map((item) => item.id === user.id ? { ...item, is_active: event.target.checked } : item))} />
                    </td>
                    <td className="px-3 py-2">
                      <button className="btn-secondary" type="button" onClick={() => saveUser(user)}>Save</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="panel p-5">
          <h2 className="font-bold">Teams</h2>
          <div className="mt-4 space-y-3">
            {teams.map((team) => (
              <div key={team.id} className="rounded-lg bg-slate-50 p-4 dark:bg-slate-800">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div>
                    <p className="font-semibold">{team.name}</p>
                    <p className="text-sm text-slate-500">{team.member_count} members</p>
                  </div>
                  <select className="input w-full sm:w-56" defaultValue="" onChange={(event) => event.target.value && promote(team.id, event.target.value)}>
                    <option value="">Promote leader</option>
                    {users.map((user) => <option key={user.id} value={user.id}>{user.full_name}</option>)}
                  </select>
                </div>
              </div>
            ))}
          </div>
        </div>
        <div className="panel p-5">
          <h2 className="font-bold">Manage tasks</h2>
          <div className="mt-4 space-y-3">
            {tasks.map((task) => (
              <div key={task.id} className="rounded-lg bg-slate-50 p-4 dark:bg-slate-800">
                <div className="grid gap-3 lg:grid-cols-[1fr_110px_190px_auto] lg:items-center">
                  <input className="input" value={task.title} onChange={(event) => setTasks(tasks.map((item) => item.id === task.id ? { ...item, title: event.target.value } : item))} />
                  <input className="input" type="number" min="1" value={task.points} onChange={(event) => setTasks(tasks.map((item) => item.id === task.id ? { ...item, points: event.target.value } : item))} />
                  <input className="input" type="datetime-local" value={toDateTimeLocal(task.deadline)} onChange={(event) => setTasks(tasks.map((item) => item.id === task.id ? { ...item, deadline: event.target.value } : item))} />
                  <div className="flex gap-2">
                    <button className="btn-secondary" type="button" onClick={() => saveTask(task)}>Save</button>
                    <button className="btn-secondary" type="button" onClick={() => deleteTask(task.id)}>Delete</button>
                  </div>
                </div>
                <label className="mt-3 flex items-center gap-2 text-sm">
                  <input type="checkbox" checked={task.is_required} onChange={(event) => setTasks(tasks.map((item) => item.id === task.id ? { ...item, is_required: event.target.checked } : item))} />
                  Required · {task.category}
                </label>
              </div>
            ))}
            {tasks.length === 0 && <p className="text-sm text-slate-500">No tasks yet.</p>}
          </div>
        </div>
        <div className="panel p-5">
          <h2 className="font-bold">Manage announcements</h2>
          <div className="mt-4 space-y-3">
            {announcements.map((announcement) => (
              <div key={announcement.id} className="rounded-lg bg-slate-50 p-4 dark:bg-slate-800">
                <input className="input" value={announcement.title} onChange={(event) => setAnnouncements(announcements.map((item) => item.id === announcement.id ? { ...item, title: event.target.value } : item))} />
                <textarea className="input mt-3 min-h-20" value={announcement.body} onChange={(event) => setAnnouncements(announcements.map((item) => item.id === announcement.id ? { ...item, body: event.target.value } : item))} />
                <div className="mt-3 flex flex-wrap gap-2">
                  <button className="btn-secondary" type="button" onClick={() => saveAnnouncement(announcement)}>Save</button>
                  <button className="btn-secondary" type="button" onClick={() => toggleAnnouncement(announcement)}>{announcement.is_pinned ? "Unpin" : "Pin"}</button>
                  <button className="btn-secondary" type="button" onClick={() => deleteAnnouncement(announcement.id)}>Delete</button>
                </div>
              </div>
            ))}
            {announcements.length === 0 && <p className="text-sm text-slate-500">No announcements yet.</p>}
          </div>
        </div>
        <div className="panel p-5">
          <h2 className="font-bold">Top members</h2>
          <div className="mt-4 space-y-3">
            {statistics?.top_members?.map((member) => (
              <div key={member.id} className="flex items-center justify-between rounded-lg bg-slate-50 p-4 dark:bg-slate-800">
                <p className="font-semibold">{member.full_name}</p>
                <p className="font-bold text-teal-700 dark:text-teal-300">{member.points} pts</p>
              </div>
            ))}
          </div>
        </div>
      </section>
    </>
  );
}

function AdminForm({ title, children, onSubmit }) {
  return (
    <form className="panel p-5" onSubmit={onSubmit}>
      <h2 className="mb-4 font-bold">{title}</h2>
      <div className="space-y-3">{children}</div>
      <button className="btn-primary mt-4 w-full">Save</button>
    </form>
  );
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
