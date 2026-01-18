import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { getInstitutions, createInstitution } from '../services/api';

interface Institution {
    id: number;
    name: string;
    slug: string;
    email: string | null;
    subscription_tier: string;
    max_students: number;
    is_active: boolean;
}

export default function SuperAdminPage() {
    const [institutions, setInstitutions] = useState<Institution[]>([]);
    const [showModal, setShowModal] = useState(false);
    const [newInst, setNewInst] = useState({ name: '', slug: '', email: '' });
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchInstitutions();
    }, []);

    const fetchInstitutions = async () => {
        try {
            const data = await getInstitutions();
            setInstitutions(data);
        } catch (err) {
            console.error('Failed to fetch institutions', err);
        } finally {
            setLoading(false);
        }
    };

    const handleCreate = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            await createInstitution(newInst);
            setShowModal(false);
            setNewInst({ name: '', slug: '', email: '' });
            fetchInstitutions();
        } catch (err) {
            console.error('Failed to create institution', err);
        }
    };

    const handleLogout = () => {
        localStorage.removeItem('token');
        window.location.href = '/login';
    };

    return (
        <div className="min-h-screen bg-gray-900 text-white">
            {/* Header */}
            <header className="bg-gray-800 shadow">
                <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
                    <h1 className="text-2xl font-bold">🏛️ SuperAdmin Panel</h1>
                    <nav className="flex gap-4 items-center">
                        <Link to="/superadmin" className="text-blue-400 font-medium">Institutions</Link>
                        <Link to="/superadmin/analytics" className="text-gray-400 hover:text-blue-400">Global Analytics</Link>
                        <button onClick={handleLogout} className="text-red-400 hover:text-red-300">Logout</button>
                    </nav>
                </div>
            </header>

            {/* Main */}
            <main className="max-w-7xl mx-auto px-4 py-8">
                <div className="flex justify-between items-center mb-6">
                    <h2 className="text-xl font-bold">All Institutions</h2>
                    <button
                        onClick={() => setShowModal(true)}
                        className="bg-blue-600 px-4 py-2 rounded-lg hover:bg-blue-700 transition"
                    >
                        + Add Institution
                    </button>
                </div>

                {loading ? (
                    <p className="text-gray-400">Loading...</p>
                ) : (
                    <div className="bg-gray-800 rounded-xl overflow-hidden">
                        <table className="w-full">
                            <thead className="bg-gray-700">
                                <tr>
                                    <th className="text-left p-4">ID</th>
                                    <th className="text-left p-4">Name</th>
                                    <th className="text-left p-4">Slug</th>
                                    <th className="text-left p-4">Tier</th>
                                    <th className="text-left p-4">Max Students</th>
                                    <th className="text-left p-4">Status</th>
                                    <th className="text-left p-4">Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {institutions.map((inst) => (
                                    <tr key={inst.id} className="border-t border-gray-700 hover:bg-gray-750">
                                        <td className="p-4">{inst.id}</td>
                                        <td className="p-4 font-medium">{inst.name}</td>
                                        <td className="p-4 text-gray-400">{inst.slug}</td>
                                        <td className="p-4">
                                            <span className={`px-2 py-1 rounded text-xs ${inst.subscription_tier === 'enterprise' ? 'bg-purple-600' :
                                                    inst.subscription_tier === 'pro' ? 'bg-blue-600' :
                                                        inst.subscription_tier === 'basic' ? 'bg-green-600' : 'bg-gray-600'
                                                }`}>
                                                {inst.subscription_tier.toUpperCase()}
                                            </span>
                                        </td>
                                        <td className="p-4">{inst.max_students}</td>
                                        <td className="p-4">
                                            {inst.is_active ? (
                                                <span className="text-green-400">Active</span>
                                            ) : (
                                                <span className="text-red-400">Inactive</span>
                                            )}
                                        </td>
                                        <td className="p-4">
                                            <Link to={`/superadmin/institutions/${inst.id}`} className="text-blue-400 hover:underline">
                                                Manage
                                            </Link>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </main>

            {/* Modal */}
            {showModal && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
                    <div className="bg-gray-800 rounded-xl p-6 w-full max-w-md">
                        <h3 className="text-xl font-bold mb-4">Add New Institution</h3>
                        <form onSubmit={handleCreate} className="space-y-4">
                            <input
                                type="text"
                                placeholder="Institution Name"
                                value={newInst.name}
                                onChange={(e) => setNewInst({ ...newInst, name: e.target.value })}
                                className="w-full px-4 py-2 bg-gray-700 rounded-lg"
                                required
                            />
                            <input
                                type="text"
                                placeholder="Slug (e.g., harvard-uni)"
                                value={newInst.slug}
                                onChange={(e) => setNewInst({ ...newInst, slug: e.target.value })}
                                className="w-full px-4 py-2 bg-gray-700 rounded-lg"
                                required
                            />
                            <input
                                type="email"
                                placeholder="Admin Email"
                                value={newInst.email}
                                onChange={(e) => setNewInst({ ...newInst, email: e.target.value })}
                                className="w-full px-4 py-2 bg-gray-700 rounded-lg"
                            />
                            <div className="flex gap-2">
                                <button type="submit" className="flex-1 bg-blue-600 py-2 rounded-lg hover:bg-blue-700">
                                    Create
                                </button>
                                <button type="button" onClick={() => setShowModal(false)} className="flex-1 bg-gray-600 py-2 rounded-lg hover:bg-gray-500">
                                    Cancel
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
}
