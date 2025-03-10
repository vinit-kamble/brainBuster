### 1. Welcome Screen

**Options Available:**
- **Login/Signup:**  
  Users can either log in to an existing account or sign up if they are new.  
- **Enter Quiz Code:**  
  A direct entry point for users who have a quiz code, allowing them to join a quiz without going through account creation (if permitted).

**Key Considerations:**
- **Clear UI:**  
  Use prominent buttons for “Login,” “Signup,” and “Enter Quiz Code” to minimize confusion.
- **Guided Experience:**  
  Optionally, include a brief intro or visual guide to explain the options.
  
---

### 2. Main Dashboard

**Core Features:**
- **Create Quiz:**  
  A button that directs users to the quiz creation process.
- **Enter Quiz Code:**  
  Another entry point for joining quizzes by entering a unique code.
- **Quiz Lists:**  
  Search & Filter: If users have many quizzes, add search or filter options to quickly find “Created Quizzes” or “Participated Quizzes.”
  - **Created Quizzes:**  
    A list of quizzes the user has created.
  - **Participated Quizzes:**  
    A list of quizzes where the user has participated.
    
**User Flow on Dashboard:**
- Once logged in, the user lands on the dashboard where they see a summary of their activities.
- The navigation menu could include quick links to “My Profile,” “Settings,” and a “Help” section.

---

### 3. Create Quiz Flow

**Step-by-Step Process:**

1. **Initiate Quiz Creation:**
   - **Accessing the Page:**  
     User taps the “Create Quiz” button on the dashboard.
   - **Quiz Basic Details:**  
     - **Quiz Title & Description:**  
       Input fields for naming the quiz. Options to define the quiz’s visibility duration and time limits per question.
     - **Quiz Code Generation:**  
       The system can either auto-generate a unique code or allow the user to set one.
   
2. **Adding Questions:**
   - **Question Types:**  
     multiple choice.
   - **Question Details:**  
     Each question screen allows:
     - Inputting the question text.
     - Adding possible answer options.
     - Marking the correct answer(s).
     - Optionally setting a timer for that specific question.
   - **Managing Questions:**  
     Ability to edit, or delete questions after quiz creation.
   - **Preview Mode:**  
     Let the creator preview the quiz to ensure it flows as intended.

3. **User Guidance:**
   - **Error Handling:** 
     Incorporate validation and user-friendly error messages (e.g., if required fields are left empty).