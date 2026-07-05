# LLM Output

=== FILE: src/App.jsx ===
import React, { useState, useEffect, useCallback, useRef } from 'react';
import { HashRouter, useNavigate } from 'react-router-dom';
import { FiPlus, FiEdit, FiTrash, FiChevronRight, FiChevronLeft } from 'lucide-react';
import { ToastContainer, toast } from 'react-toastify';
import { format } from 'date-fns';
import { useForm } from 'react-hook-form';
import clsx from 'clsx';

const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const App = () => {
  const navigate = useNavigate();
  const [students, setStudents] = useState([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isDarkMode, setIsDarkMode] = useState(true);
  const [stats, setStats] = useState({
    totalStudents: 0,
    classAverage: 0,
    passingCount: 0,
    failingCount: 0
  });

  const { register, handleSubmit, reset } = useForm();

  const fetchStudents = useCallback(async () => {
    try {
      const response = await fetch(`${BASE_URL}/students`);
      const data = await response.json();
      const safeData = Array.isArray(data) ? data : (data?.items || []);
      setStudents(safeData);
      calculateStats(safeData);
    } catch (error) {
      console.error(error);
    }
  }, []);

  const calculateStats = (students) => {
    const totalStudents = students.length;
    const classAverage = students.reduce((acc, student) => acc + student.average, 0) / totalStudents;
    const passingCount = students.filter((student) => student.average >= 50).length;
    const failingCount = totalStudents - passingCount;
    setStats({ totalStudents, classAverage, passingCount, failingCount });
  };

  const addStudent = async (data) => {
    try {
      const response = await fetch(`${BASE_URL}/students`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });
      const student = await response.json();
      setStudents((prevStudents) => [...prevStudents, student]);
      calculateStats([...students, student]);
      setIsModalOpen(false);
      reset();
    } catch (error) {
      console.error(error);
    }
  };

  const sortStudents = (students, sortBy) => {
    if (sortBy === 'name') {
      return students.sort((a, b) => a.name.localeCompare(b.name));
    } else if (sortBy === 'average') {
      return students.sort((a, b) => b.average - a.average);
    }
  };

  const getGrade = (average) => {
    if (average >= 90) return 'A+';
    if (average >= 80) return 'A';
    if (average >= 70) return 'B';
    if (average >= 60) return 'C';
    if (average >= 50) return 'D';
    return 'F';
  };

  const getColor = (grade) => {
    switch (grade) {
      case 'A+':
        return 'bg-green-500 text-white';
      case 'A':
        return 'bg-blue-500 text-white';
      case 'B':
        return 'bg-yellow-500 text-black';
      case 'C':
        return 'bg-orange-500 text-black';
      case 'D':
        return 'bg-red-500 text-white';
      default:
        return 'bg-red-500 text-white';
    }
  };

  useEffect(() => {
    fetchStudents();
  }, [fetchStudents]);

  const handleToggleDarkMode = () => {
    setIsDarkMode((prevDarkMode) => !prevDarkMode);
  };

  return (
    <HashRouter>
      <div className={clsx('h-screen w-screen', isDarkMode ? 'bg-gray-900' : 'bg-gray-100')}>
        <header className="flex justify-between items-center py-4 px-6">
          <h1 className="text-2xl font-bold text-white">Student Tracker</h1>
          <button
            className={clsx('bg-gray-800 text-white hover:bg-gray-700 transition-all duration-300', isDarkMode ? 'mr-4' : 'ml-4')}
            onClick={handleToggleDarkMode}
          >
            {isDarkMode ? <FiChevronRight size={20} /> : <FiChevronLeft size={20} />}
          </button>
        </header>
        <main className="flex flex-col items-center py-6 px-6">
          <h2 className="text-xl font-bold text-white mb-4">Students</h2>
          <table className="w-full text-white">
            <thead>
              <tr>
                <th className="px-4 py-2">Name</th>
                <th className="px-4 py-2">Roll No</th>
                <th className="px-4 py-2">Math</th>
                <th className="px-4 py-2">Science</th>
                <th className="px-4 py-2">English</th>
                <th className="px-4 py-2">History</th>
                <th className="px-4 py-2">Average</th>
                <th className="px-4 py-2">Grade</th>
              </tr>
            </thead>
            <tbody>
              {sortStudents(students, 'average').map((student) => (
                <tr key={student.id}>
                  <td className="px-4 py-2">{student.name}</td>
                  <td className="px-4 py-2">{student.rollNo}</td>
                  <td className="px-4 py-2">{student.math}</td>
                  <td className="px-4 py-2">{student.science}</td>
                  <td className="px-4 py-2">{student.english}</td>
                  <td className="px-4 py-2">{student.history}</td>
                  <td className="px-4 py-2">{student.average.toFixed(2)}</td>
                  <td className="px-4 py-2">
                    <span
                      className={clsx('px-2 py-1 rounded', getColor(getGrade(student.average)))}
                    >
                      {getGrade(student.average)}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className="flex justify-between items-center py-4">
            <p className="text-white">Total Students: {stats.totalStudents}</p>
            <p className="text-white">Class Average: {stats.classAverage.toFixed(2)}</p>
            <p className="text-white">Passing Count: {stats.passingCount}</p>
            <p className="text-white">Failing Count: {stats.failingCount}</p>
          </div>
          <button
            className="bg-gray-800 text-white hover:bg-gray-700 transition-all duration-300"
            onClick={() => setIsModalOpen(true)}
          >
            <FiPlus size={20} /> Add Student
          </button>
        </main>
        {isModalOpen && (
          <div className="fixed top-0 left-0 w-full h-full bg-gray-900 bg-opacity-50 flex items-center justify-center">
            <form
              className="bg-gray-800 text-white p-6 rounded"
              onSubmit={handleSubmit(addStudent)}
            >
              <h2 className="text-2xl font-bold mb-4">Add Student</h2>
              <div className="flex flex-col mb-4">
                <label className="mb-2">Name</label>
                <input
                  type="text"
                  {...register('name')}
                  className="bg-gray-700 text-white p-2 rounded"
                />
              </div>
              <div className="flex flex-col mb-4">
                <label className="mb-2">Roll No</label>
                <input
                  type="number"
                  {...register('rollNo')}
                  className="bg-gray-700 text-white p-2 rounded"
                />
              </div>
              <div className="flex flex-col mb-4">
                <label className="mb-2">Math</label>
                <input
                  type="number"
                  {...register('math')}
                  min="0"
                  max="100"
                  className="bg-gray-700 text-white p-2 rounded"
                />
              </div>
              <div className="flex flex-col mb-4">
                <label className="mb-2">Science</label>
                <input
                  type="number"
                  {...register('science')}
                  min="0"
                  max="100"
                  className="bg-gray-700 text-white p-2 rounded"
                />
              </div>
              <div className="flex flex-col mb-4">
                <label className="mb-2">English</label>
                <input
                  type="number"
                  {...register('english')}
                  min="0"
                  max="100"
                  className="bg-gray-700 text-white p-2 rounded"
                />
              </div>
              <div className="flex flex-col mb-4">
                <label className="mb-2">History</label>
                <input
                  type="number"
                  {...register('history')}
                  min="0"
                  max="100"
                  className="bg-gray-700 text-white p-2 rounded"
                />
              </div>
              <button
                type="submit"
                className="bg-gray-700 text-white hover:bg-gray-600 transition-all duration-300"
              >
                Add Student
              </button>
            </form>
          </div>
        )}
        <ToastContainer />
      </div>
    </HashRouter>
  );
};

export default App;
=== END ===