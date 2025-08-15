import React, { useState, useEffect, useRef } from 'react';
import './calendar.css';

const CalendarDatePicker = ({ onDateSelect, placeholder = "Pick a date" }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [currentDate, setCurrentDate] = useState(new Date());
  const [selectedDate, setSelectedDate] = useState(null);
  const [selectedDateStr, setSelectedDateStr] = useState('');
  const dropdownRef = useRef(null);
  
  const monthNames = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
  ];
  
  const dayNames = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const formatDate = (date) => {
    // Use local date components to avoid timezone issues
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  };

  const formatDisplayDate = (date) => {
    return date.toLocaleDateString('en-GB', {
      day: 'numeric',
      month: 'short',
      year: 'numeric'
    });
  };

  const handleDateSelect = (dateStr) => {
    // Parse the date string and create a local date object
    const [year, month, day] = dateStr.split('-').map(Number);
    const date = new Date(year, month - 1, day); // month is 0-indexed
    
    setSelectedDate(date);
    setSelectedDateStr(dateStr);
    setIsOpen(false);
    
    // Call parent callback with selected date
    if (onDateSelect) {
      onDateSelect(dateStr, date);
    }
  };

  const clearSelection = () => {
    setSelectedDate(null);
    setSelectedDateStr('');
    if (onDateSelect) {
      onDateSelect(null, null);
    }
  };

  const previousMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1));
  };

  const nextMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1));
  };

  const renderCalendar = () => {
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();
    
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const firstDayOfWeek = firstDay.getDay();
    const daysInMonth = lastDay.getDate();
    
    const calendarDays = [];
    
    // Add empty cells for days before month starts
    for (let i = 0; i < firstDayOfWeek; i++) {
      const prevMonthDate = new Date(year, month, -firstDayOfWeek + i + 1);
      calendarDays.push({
        date: prevMonthDate,
        day: prevMonthDate.getDate(),
        isCurrentMonth: false,
        dateStr: formatDate(prevMonthDate)
      });
    }
    
    // Add days of current month
    const today = new Date();
    const todayStr = formatDate(today);
    for (let day = 1; day <= daysInMonth; day++) {
      const date = new Date(year, month, day);
      const dateStr = formatDate(date);
      calendarDays.push({
        date,
        day,
        isCurrentMonth: true,
        dateStr,
        isToday: dateStr === todayStr,
        isSelected: selectedDateStr === dateStr
      });
    }
    
    // Add empty cells for days after month ends
    const totalCells = Math.ceil((firstDayOfWeek + daysInMonth) / 7) * 7;
    const remainingCells = totalCells - (firstDayOfWeek + daysInMonth);
    for (let i = 1; i <= remainingCells; i++) {
      const nextMonthDate = new Date(year, month + 1, i);
      calendarDays.push({
        date: nextMonthDate,
        day: i,
        isCurrentMonth: false,
        dateStr: formatDate(nextMonthDate)
      });
    }
    
    return calendarDays;
  };

  const calendarDays = renderCalendar();

  return (
    <div className="calendar-container" ref={dropdownRef}>
      {/* Dropdown Trigger */}
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="dropdown-button"
      >
        <span className={selectedDate ? "selected-text" : "placeholder-text"}>
          {selectedDate ? formatDisplayDate(selectedDate) : placeholder}
        </span>
        <svg
          className={`chevron ${isOpen ? 'open' : ''}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {/* Calendar Dropdown */}
      {isOpen && (
        <div className="dropdown">
          {/* Calendar Header */}
          <div className="calendar-header">
            <button
              onClick={previousMonth}
              className="nav-button"
            >
              ← Prev
            </button>
            <h3 className="month-title">
              {monthNames[currentDate.getMonth()]} {currentDate.getFullYear()}
            </h3>
            <button
              onClick={nextMonth}
              className="nav-button"
            >
              Next →
            </button>
          </div>

          {/* Calendar Grid */}
          <div className="calendar-grid">
            {/* Day Headers */}
            {dayNames.map(day => (
              <div key={day} className="day-header">
                {day}
              </div>
            ))}

            {/* Calendar Days */}
            {calendarDays.map((dayObj, index) => {
              const classNames = [
                'day-button',
                dayObj.isCurrentMonth ? 'current-month' : 'other-month',
                dayObj.isToday ? 'today' : '',
                dayObj.isSelected ? 'selected' : ''
              ].filter(Boolean).join(' ');

              return (
                <button
                  key={index}
                  onClick={() => handleDateSelect(dayObj.dateStr)}
                  className={classNames}
                >
                  {dayObj.day}
                </button>
              );
            })}
          </div>

          {/* Action Buttons */}
          <div className="action-buttons">
            <button
              onClick={clearSelection}
              className="clear-button"
            >
              Clear
            </button>
            <button
              onClick={() => setIsOpen(false)}
              className="done-button"
            >
              Done
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default CalendarDatePicker;