import { Navigate, Outlet, Route, Routes } from "react-router-dom";

import AppLayout from "./layouts/AppLayout.jsx";
import AdminPanel from "./pages/AdminPanel.jsx";
import Announcements from "./pages/Announcements.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import Leaderboard from "./pages/Leaderboard.jsx";
import Login from "./pages/Login.jsx";
import Profile from "./pages/Profile.jsx";
import Submissions from "./pages/Submissions.jsx";
import Tasks from "./pages/Tasks.jsx";
import { useAuth } from "./hooks/useAuth.jsx";

function ProtectedRoute() {
  const { user, loading } = useAuth();
  if (loading) {
    return <div className="grid min-h-screen place-items-center bg-slate-50 text-slate-700 dark:bg-slate-950 dark:text-slate-200">Loading Mawahib...</div>;
  }
  return user ? <Outlet /> : <Navigate to="/login" replace />;
}

function AdminRoute() {
  const { isAdmin, loading } = useAuth();
  if (loading) {
    return null;
  }
  return isAdmin ? <Outlet /> : <Navigate to="/" replace />;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route element={<ProtectedRoute />}>
        <Route element={<AppLayout />}>
          <Route index element={<Dashboard />} />
          <Route path="tasks" element={<Tasks />} />
          <Route path="submissions" element={<Submissions />} />
          <Route path="leaderboard" element={<Leaderboard />} />
          <Route path="announcements" element={<Announcements />} />
          <Route path="profile" element={<Profile />} />
          <Route element={<AdminRoute />}>
            <Route path="admin" element={<AdminPanel />} />
          </Route>
        </Route>
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

