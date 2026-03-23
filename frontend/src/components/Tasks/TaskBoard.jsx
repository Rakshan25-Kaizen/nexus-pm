import React, { useEffect, useState } from 'react';
import useNexusStore from '../../store/useNexusStore';
import { getTasks, createTask } from '../../api/client';
import TaskCard from './TaskCard';
import AssignModal from './AssignModal';
import { CirclePlus, UserCheck } from 'lucide-react';

const columns = ['todo', 'in_progress', 'done', 'blocked'];
const columnLabels = { todo: 'TODO', in_progress: 'IN PROGRESS', done: 'DONE', blocked: 'BLOCKED' };
const columnColors = { todo: 'border-gray-600', in_progress: 'border-blue-500', done: 'border-green-500', blocked: 'border-red-500' };

export default function TaskBoard() {
  const { tasks, setTasks, projectId } = useNexusStore();
  const [showAssign, setShowAssign] = useState(false);
  const [showAddTask, setShowAddTask] = useState(false);
  const [newTask, setNewTask] = useState({ title: '', category: 'Backend', complexity: 'medium' });

  useEffect(() => { getTasks(projectId).then(setTasks).catch(() => {}); }, [projectId]);

  const handleAddTask = async () => {
    if (!newTask.title) return;
    try {
      const t = await createTask({ ...newTask, project_id: projectId });
      useNexusStore.getState().addTask(t);
      setNewTask({ title: '', category: 'Backend', complexity: 'medium' });
      setShowAddTask(false);
    } catch {}
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Task Board</h1>
        <div className="flex gap-2">
          <button onClick={() => setShowAddTask(!showAddTask)} className="px-4 py-2 bg-gray-800 rounded-lg text-sm hover:bg-gray-700 transition flex items-center gap-1.5">
            <CirclePlus size={16} className="text-green-400" />
            <span>New Task</span>
          </button>
          <button onClick={() => setShowAssign(true)} className="px-4 py-2 bg-accent rounded-lg text-sm hover:bg-blue-600 transition flex items-center gap-1.5">
            <UserCheck size={16} />
            <span>Assign Task</span>
          </button>
        </div>
      </div>

      {showAddTask && (
        <div className="bg-gray-900 border border-gray-700 rounded-xl p-4 mb-4 flex gap-3 items-end">
          <input value={newTask.title} onChange={(e) => setNewTask({...newTask, title: e.target.value})} placeholder="Task title" className="flex-1 bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm" />
          <select value={newTask.category} onChange={(e) => setNewTask({...newTask, category: e.target.value})} className="bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm">
            {['Backend','Frontend','ML','Testing','Design','DevOps','General'].map(c => <option key={c}>{c}</option>)}
          </select>
          <select value={newTask.complexity} onChange={(e) => setNewTask({...newTask, complexity: e.target.value})} className="bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm">
            {['low','medium','high'].map(c => <option key={c}>{c}</option>)}
          </select>
          <button onClick={handleAddTask} className="px-4 py-2 bg-green-600 rounded text-sm hover:bg-green-700 transition">Add</button>
        </div>
      )}

      <div className="grid grid-cols-4 gap-4">
        {columns.map((col) => {
          const colTasks = tasks.filter(t => t.status === col);
          return (
            <div key={col} className={`bg-gray-900/30 rounded-xl border-t-2 ${columnColors[col]} p-3 min-h-[400px]`}>
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-sm font-semibold text-gray-300">{columnLabels[col]}</h3>
                <span className="text-xs bg-gray-800 px-2 py-0.5 rounded">{colTasks.length}</span>
              </div>
              <div className="space-y-2">
                {colTasks.map(t => <TaskCard key={t.id} task={t} />)}
              </div>
            </div>
          );
        })}
      </div>
      {showAssign && <AssignModal onClose={() => setShowAssign(false)} />}
    </div>
  );
}
