import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { getAnalyticsOverview, getDailyStats } from '../services/api';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface OverviewData {
    period_days: number;
    total_sessions: number;
    total_present: number;
    total_absent: number;
    total_late: number;
    overall_attendance_rate: number;
}

interface DailyData {
    date: string;
    total_sessions: number;
    total_present: number;
    total_absent: number;
    attendance_rate: number;
}

export default function DashboardPage() {
    const [overview, setOverview] = useState<OverviewData | null>(null);
    const [dailyStats, setDailyStats] = useState<DailyData[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const [overviewData, dailyData] = await Promise.all([
                    getAnalyticsOverview(30),
                    getDailyStats(7),
                ]);
                setOverview(overviewData);
                setDailyStats(dailyData.reverse());
            } catch (err) {
                console.error('Failed to fetch analytics', err);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, []);

    const handleLogout = () => {
        localStorage.removeItem('token');
        window.location.href = '/login';
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-gray-100 flex items-center justify-center">
                <div className="text-xl text-gray-600">Loading...</div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-100">
            {/* Header */}
            <header className="bg-white shadow">
                <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
                    <h1 className="text-2xl font-bold text-gray-800">Smart Attendance</h1>
                    <nav className="flex gap-4 items-center">
                        <Link to="/dashboard" className="text-blue-600 font-medium">Dashboard</Link>
                        <Link to="/students" className="text-gray-600 hover:text-blue-600">Students</Link>
                        <Link to="/courses" className="text-gray-600 hover:text-blue-600">Courses</Link>
                        <Link to="/sessions" className="text-gray-600 hover:text-blue-600">Sessions</Link>
                        <button onClick={handleLogout} className="text-red-600 hover:text-red-700">Logout</button>
                    </nav>
                </div>
            </header>

            {/* Main Content */}
            <main className="max-w-7xl mx-auto px-4 py-8">
                {/* Stats Cards */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                    <div className="bg-white rounded-xl shadow p-6">
                        <h3 className="text-gray-500 text-sm font-medium">Total Sessions</h3>
                        <p className="text-3xl font-bold text-gray-800 mt-2">{overview?.total_sessions || 0}</p>
                    </div>
                    <div className="bg-white rounded-xl shadow p-6">
                        <h3 className="text-gray-500 text-sm font-medium">Total Present</h3>
                        <p className="text-3xl font-bold text-green-600 mt-2">{overview?.total_present || 0}</p>
                    </div>
                    <div className="bg-white rounded-xl shadow p-6">
                        <h3 className="text-gray-500 text-sm font-medium">Total Absent</h3>
                        <p className="text-3xl font-bold text-red-600 mt-2">{overview?.total_absent || 0}</p>
                    </div>
                    <div className="bg-white rounded-xl shadow p-6">
                        <h3 className="text-gray-500 text-sm font-medium">Attendance Rate</h3>
                        <p className="text-3xl font-bold text-blue-600 mt-2">{overview?.overall_attendance_rate || 0}%</p>
                    </div>
                </div>

                {/* Chart */}
                <div className="bg-white rounded-xl shadow p-6 mb-8">
                    <h2 className="text-xl font-bold text-gray-800 mb-4">Weekly Attendance Trend</h2>
                    <div className="h-80">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={dailyStats}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="date" />
                                <YAxis />
                                <Tooltip />
                                <Bar dataKey="total_present" fill="#22c55e" name="Present" />
                                <Bar dataKey="total_absent" fill="#ef4444" name="Absent" />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Quick Actions */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <Link to="/sessions/new" className="bg-blue-600 text-white rounded-xl p-6 hover:bg-blue-700 transition">
                        <h3 className="text-xl font-bold">Start Session</h3>
                        <p className="text-blue-200 mt-2">Begin attendance capture</p>
                    </Link>
                    <Link to="/students/enroll" className="bg-green-600 text-white rounded-xl p-6 hover:bg-green-700 transition">
                        <h3 className="text-xl font-bold">Enroll Student</h3>
                        <p className="text-green-200 mt-2">Add new student with photos</p>
                    </Link>
                    <Link to="/reports" className="bg-purple-600 text-white rounded-xl p-6 hover:bg-purple-700 transition">
                        <h3 className="text-xl font-bold">View Reports</h3>
                        <p className="text-purple-200 mt-2">Export attendance data</p>
                    </Link>
                </div>
            </main>
        </div>
    );
}
