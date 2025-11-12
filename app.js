  // Simple front-end auth using localStorage (demo only)
  document.addEventListener('DOMContentLoaded', function() {
    console.log('Auth script loading...');
    
    // Get elements
    const authModal = document.getElementById('authModal');
    const loginBtn = document.getElementById('loginBtn');
    const profileBtn = document.getElementById('profileBtn');
    const authClose = document.getElementById('authClose');
    const authForm = document.getElementById('authForm');
    const authEmail = document.getElementById('authEmail');
    const authPassword = document.getElementById('authPassword');
    const authPassword2 = document.getElementById('authPassword2');
    const authName = document.getElementById('authName');
    const profileName = document.getElementById('profileName');
    const profileDropdown = document.getElementById('profileDropdown');
    const dropdownMenu = document.getElementById('dropdownMenu');
    const profileLink = document.getElementById('profileLink');
    const settingsLink = document.getElementById('settingsLink');
    const logoutLink = document.getElementById('logoutLink');
    const profilePage = document.getElementById('profilePage');
    const profileBack = document.getElementById('profileBack');
    const logoutBtn = document.getElementById('logoutBtn');
    const adminLink = document.getElementById('adminLink');
    const adminDashboard = document.getElementById('adminDashboard');
    const adminBack = document.getElementById('adminBack');
    const totalUsers = document.getElementById('totalUsers');
    const adminUsers = document.getElementById('adminUsers');
    const usersTableBody = document.getElementById('usersTableBody');
    const adminName = document.getElementById('adminName');
    const adminEmail = document.getElementById('adminEmail');
    const adminPassword = document.getElementById('adminPassword');
    const createAdmin = document.getElementById('createAdmin');
    const authModeLogin = document.getElementById('authModeLogin');
    const authModeSignup = document.getElementById('authModeSignup');
    const authTitle = document.getElementById('authTitle');
    const authSubtitle = document.getElementById('authSubtitle');
    const authSubmit = document.getElementById('authSubmit');
    const authMessage = document.getElementById('authMessage');
    
    console.log('Elements found:', {
      authModal: !!authModal,
      loginBtn: !!loginBtn,
      profileBtn: !!profileBtn,
      authClose: !!authClose
    });

    let currentMode = 'login';

    // Mode switching
    function setMode(mode) {
      currentMode = mode;
      const isSignup = mode === 'signup';
      
      // Update tabs
      if(authModeLogin) {
        authModeLogin.classList.toggle('active', !isSignup);
        authModeLogin.setAttribute('aria-selected', String(!isSignup));
      }
      if(authModeSignup) {
        authModeSignup.classList.toggle('active', isSignup);
        authModeSignup.setAttribute('aria-selected', String(isSignup));
      }
      
      // Update title and subtitle
      if(authTitle) authTitle.textContent = isSignup ? 'Inscription' : 'Connexion';
      if(authSubtitle) authSubtitle.textContent = isSignup ? "Créez votre compte pour démarrer votre serveur." : "Connectez-vous pour gérer votre serveur.";
      if(authSubmit) authSubmit.textContent = isSignup ? "S'inscrire" : "Se connecter";
      
      // Toggle signup fields
      const signupOnly = document.querySelectorAll('.signup-only');
      signupOnly.forEach(el => { el.hidden = !isSignup; });
      
      // Required attributes
      if(authName) authName.required = isSignup;
      if(authPassword2) authPassword2.required = isSignup;
    }

    // Account management
    function getAccounts() {
      try { 
        return JSON.parse(localStorage.getItem('minehost_accounts')) || []; 
      } catch { 
        return []; 
      }
    }

    function saveAccounts(accounts) {
      localStorage.setItem('minehost_accounts', JSON.stringify(accounts));
    }

    function findAccount(email) {
      const accounts = getAccounts();
      return accounts.find(acc => acc.email === email);
    }

    function createAccount(email, password, name, role = 'user') {
      const accounts = getAccounts();
      const newAccount = { email, password, name, role, createdAt: new Date().toISOString() };
      accounts.push(newAccount);
      saveAccounts(accounts);
      return newAccount;
    }

    function validateLogin(email, password) {
      const account = findAccount(email);
      if(!account) return { success: false, message: 'Aucun compte trouvé avec cet email.' };
      if(account.password !== password) return { success: false, message: 'Mot de passe incorrect.' };
      return { success: true, account };
    }

    function validateSignup(email, password, name) {
      if(findAccount(email)) return { success: false, message: 'Un compte existe déjà avec cet email.' };
      if(password.length < 6) return { success: false, message: 'Le mot de passe doit contenir au moins 6 caractères.' };
      return { success: true };
    }

    function showMessage(text, type = 'error') {
      if(authMessage) {
        authMessage.textContent = text;
        authMessage.className = `auth-message ${type}`;
        authMessage.style.display = 'block';
        setTimeout(() => {
          authMessage.style.display = 'none';
        }, 5000);
      }
    }

    // Modal functions
    function showModal() {
      console.log('Showing modal');
      if(authModal) {
        authModal.style.display = 'flex';
      }
    }

    function hideModal() {
      console.log('Hiding modal');
      if(authModal) {
        authModal.style.display = 'none';
      }
    }

    function showProfilePage() {
      if(profilePage) {
        profilePage.style.display = 'block';
      }
    }

    function hideProfilePage() {
      if(profilePage) {
        profilePage.style.display = 'none';
      }
    }

    function showAdminDashboard() {
      if(adminDashboard) {
        adminDashboard.style.display = 'block';
        
        // Update welcome message with admin name
        const user = getUser();
        const adminWelcomeName = document.getElementById('adminWelcomeName');
        if(adminWelcomeName && user) {
          adminWelcomeName.textContent = user.name || user.email;
        }
        
        loadAdminData();
      }
    }

    function hideAdminDashboard() {
      if(adminDashboard) {
        adminDashboard.style.display = 'none';
      }
    }

    function loadAdminData() {
      const accounts = getAccounts();
      const total = accounts.length;
      const admins = accounts.filter(acc => acc.role === 'admin').length;
      
      if(totalUsers) totalUsers.textContent = total;
      if(adminUsers) adminUsers.textContent = admins;
      
      if(usersTableBody) {
        usersTableBody.innerHTML = '';
        accounts.forEach(account => {
          const row = document.createElement('tr');
          row.innerHTML = `
            <td>${account.name}</td>
            <td>${account.email}</td>
            <td><span class="role-badge role-${account.role}">${account.role.toUpperCase()}</span></td>
            <td>${new Date(account.createdAt).toLocaleDateString()}</td>
            <td>
              <button class="btn btn-primary small" onclick="openEditEmail('${account.email}')" title="Modifier l'email">✉️ Email</button>
              <button class="btn btn-ghost small" onclick="openResetPassword('${account.email}')" title="Réinitialiser le mot de passe">🔑 MDP</button>
              <button class="btn btn-danger small" onclick="deleteUser('${account.email}')" title="Supprimer">❌</button>
            </td>
          `;
          usersTableBody.appendChild(row);
        });
      }
    }

    function deleteUser(email) {
      if(confirm('Êtes-vous sûr de vouloir supprimer cet utilisateur ?')) {
        const accounts = getAccounts();
        const filteredAccounts = accounts.filter(acc => acc.email !== email);
        saveAccounts(filteredAccounts);
        loadAdminData();
        alert('Utilisateur supprimé avec succès !');
      }
    }

    // Edit Email functionality
    let currentEditingEmail = null;
    const editEmailModal = document.getElementById('editEmailModal');
    const editEmailClose = document.getElementById('editEmailClose');
    const editEmailCancel = document.getElementById('editEmailCancel');
    const editEmailForm = document.getElementById('editEmailForm');
    const editEmailOld = document.getElementById('editEmailOld');
    const editEmailNew = document.getElementById('editEmailNew');
    const editEmailMessage = document.getElementById('editEmailMessage');

    function openEditEmail(email) {
      currentEditingEmail = email;
      const account = findAccount(email);
      if(account && editEmailOld) {
        editEmailOld.value = account.email;
        if(editEmailNew) editEmailNew.value = '';
        if(editEmailMessage) editEmailMessage.style.display = 'none';
        if(editEmailModal) editEmailModal.style.display = 'flex';
      }
    }

    function closeEditEmailModal() {
      if(editEmailModal) editEmailModal.style.display = 'none';
      currentEditingEmail = null;
    }

    function showEditEmailMessage(text, type = 'error') {
      if(editEmailMessage) {
        editEmailMessage.textContent = text;
        editEmailMessage.className = `auth-message ${type}`;
        editEmailMessage.style.display = 'block';
        setTimeout(() => {
          editEmailMessage.style.display = 'none';
        }, 5000);
      }
    }

    if(editEmailClose) {
      editEmailClose.addEventListener('click', closeEditEmailModal);
    }

    if(editEmailCancel) {
      editEmailCancel.addEventListener('click', closeEditEmailModal);
    }

    if(editEmailModal) {
      editEmailModal.addEventListener('click', function(e) {
        if(e.target === editEmailModal) {
          closeEditEmailModal();
        }
      });
    }

    if(editEmailForm) {
      editEmailForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const newEmail = editEmailNew ? editEmailNew.value.trim() : '';
        
        if(!newEmail) {
          showEditEmailMessage('Veuillez entrer un nouvel email.');
          return;
        }

        if(newEmail === currentEditingEmail) {
          showEditEmailMessage('Le nouvel email est identique à l\'ancien.');
          return;
        }

        // Check if new email already exists
        if(findAccount(newEmail)) {
          showEditEmailMessage('Cet email est déjà utilisé par un autre compte.');
          return;
        }

        // Update email
        const accounts = getAccounts();
        const accountIndex = accounts.findIndex(acc => acc.email === currentEditingEmail);
        
        if(accountIndex !== -1) {
          accounts[accountIndex].email = newEmail;
          saveAccounts(accounts);
          
          // Update current user if they edited their own email
          const currentUser = getUser();
          if(currentUser && currentUser.email === currentEditingEmail) {
            currentUser.email = newEmail;
            setUser(currentUser);
            applyAuthState();
          }
          
          showEditEmailMessage('Email modifié avec succès !', 'success');
          setTimeout(() => {
            closeEditEmailModal();
            loadAdminData();
          }, 1500);
        }
      });
    }

    // Reset Password functionality
    let currentResetEmail = null;
    const resetPasswordModal = document.getElementById('resetPasswordModal');
    const resetPasswordClose = document.getElementById('resetPasswordClose');
    const resetPasswordCancel = document.getElementById('resetPasswordCancel');
    const resetPasswordForm = document.getElementById('resetPasswordForm');
    const resetPasswordUser = document.getElementById('resetPasswordUser');
    const resetPasswordNew = document.getElementById('resetPasswordNew');
    const resetPasswordConfirm = document.getElementById('resetPasswordConfirm');
    const resetPasswordMessage = document.getElementById('resetPasswordMessage');

    function openResetPassword(email) {
      currentResetEmail = email;
      const account = findAccount(email);
      if(account && resetPasswordUser) {
        resetPasswordUser.value = `${account.name} (${account.email})`;
        if(resetPasswordNew) resetPasswordNew.value = '';
        if(resetPasswordConfirm) resetPasswordConfirm.value = '';
        if(resetPasswordMessage) resetPasswordMessage.style.display = 'none';
        if(resetPasswordModal) resetPasswordModal.style.display = 'flex';
      }
    }

    function closeResetPasswordModal() {
      if(resetPasswordModal) resetPasswordModal.style.display = 'none';
      currentResetEmail = null;
    }

    function showResetPasswordMessage(text, type = 'error') {
      if(resetPasswordMessage) {
        resetPasswordMessage.textContent = text;
        resetPasswordMessage.className = `auth-message ${type}`;
        resetPasswordMessage.style.display = 'block';
        setTimeout(() => {
          resetPasswordMessage.style.display = 'none';
        }, 5000);
      }
    }

    if(resetPasswordClose) {
      resetPasswordClose.addEventListener('click', closeResetPasswordModal);
    }

    if(resetPasswordCancel) {
      resetPasswordCancel.addEventListener('click', closeResetPasswordModal);
    }

    if(resetPasswordModal) {
      resetPasswordModal.addEventListener('click', function(e) {
        if(e.target === resetPasswordModal) {
          closeResetPasswordModal();
        }
      });
    }

    if(resetPasswordForm) {
      resetPasswordForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const newPassword = resetPasswordNew ? resetPasswordNew.value.trim() : '';
        const confirmPassword = resetPasswordConfirm ? resetPasswordConfirm.value.trim() : '';
        
        if(!newPassword || !confirmPassword) {
          showResetPasswordMessage('Veuillez remplir tous les champs.');
          return;
        }

        if(newPassword.length < 6) {
          showResetPasswordMessage('Le mot de passe doit contenir au moins 6 caractères.');
          return;
        }

        if(newPassword !== confirmPassword) {
          showResetPasswordMessage('Les mots de passe ne correspondent pas.');
          return;
        }

        // Update password
        const accounts = getAccounts();
        const accountIndex = accounts.findIndex(acc => acc.email === currentResetEmail);
        
        if(accountIndex !== -1) {
          accounts[accountIndex].password = newPassword;
          saveAccounts(accounts);
          
          showResetPasswordMessage('Mot de passe réinitialisé avec succès !', 'success');
          setTimeout(() => {
            closeResetPasswordModal();
          }, 1500);
        }
      });
    }

    // Auth state management
    function getUser() {
      try { 
        return JSON.parse(localStorage.getItem('minehost_user')) || null; 
      } catch { 
        return null; 
      }
    }

    function setUser(user) {
      localStorage.setItem('minehost_user', JSON.stringify(user));
    }

    function getUserRole() {
      const user = getUser();
      return user ? user.role : null;
    }

    function isAdmin() {
      return getUserRole() === 'admin';
    }

    function clearUser() {
      localStorage.removeItem('minehost_user');
    }

    function applyAuthState() {
      const user = getUser();
      if(user) {
        if(loginBtn) loginBtn.style.display = 'none';
        if(profileDropdown) profileDropdown.style.display = 'inline-block';
        if(profileName) {
          const roleBadge = user.role === 'admin' ? ' [ADMIN]' : '';
          profileName.textContent = (user.name || user.email) + roleBadge;
        }
        // Show admin link if user is admin
        if(adminLink) {
          adminLink.style.display = user.role === 'admin' ? 'block' : 'none';
        }
      } else {
        if(loginBtn) loginBtn.style.display = 'inline-flex';
        if(profileDropdown) profileDropdown.style.display = 'none';
        if(profileName) profileName.textContent = '';
        if(adminLink) adminLink.style.display = 'none';
      }
    }

    // Event listeners
    if(loginBtn) {
      loginBtn.addEventListener('click', function() {
        console.log('Login button clicked');
        setMode('login');
        showModal();
      });
    }

    // Tab switching
    if(authModeLogin) {
      authModeLogin.addEventListener('click', function() { setMode('login'); });
    }
    
    if(authModeSignup) {
      authModeSignup.addEventListener('click', function() { setMode('signup'); });
    }

    if(authClose) {
      authClose.addEventListener('click', hideModal);
    }

    // Fermer la modale en cliquant à l'extérieur
    if(authModal) {
      authModal.addEventListener('click', function(e) {
        // Fermer uniquement si on clique sur le backdrop (pas sur la modale elle-même)
        if(e.target === authModal) {
          hideModal();
        }
      });
    }

    // Dropdown menu functionality
    if(profileBtn) {
      profileBtn.addEventListener('click', function(e) {
        e.stopPropagation();
        if(dropdownMenu) {
          dropdownMenu.classList.toggle('show');
        }
      });
    }

    // Close dropdown when clicking outside
    document.addEventListener('click', function(e) {
      if(dropdownMenu && !profileDropdown.contains(e.target)) {
        dropdownMenu.classList.remove('show');
      }
    });

    // Dropdown menu items
    if(profileLink) {
      profileLink.addEventListener('click', function(e) {
        e.preventDefault();
        showProfilePage();
        if(dropdownMenu) dropdownMenu.classList.remove('show');
      });
    }

    if(settingsLink) {
      settingsLink.addEventListener('click', function(e) {
        e.preventDefault();
        showProfilePage();
        if(dropdownMenu) dropdownMenu.classList.remove('show');
      });
    }

    if(adminLink) {
      adminLink.addEventListener('click', function(e) {
        e.preventDefault();
        showAdminDashboard();
        if(dropdownMenu) dropdownMenu.classList.remove('show');
      });
    }

    if(adminBack) {
      adminBack.addEventListener('click', hideAdminDashboard);
    }

    if(createAdmin) {
      createAdmin.addEventListener('click', function() {
        const name = adminName ? adminName.value.trim() : '';
        const email = adminEmail ? adminEmail.value.trim() : '';
        const password = adminPassword ? adminPassword.value.trim() : '';
        
        if(!name || !email || !password) {
          alert('Veuillez remplir tous les champs.');
          return;
        }
        
        if(password.length < 6) {
          alert('Le mot de passe doit contenir au moins 6 caractères.');
          return;
        }
        
        if(findAccount(email)) {
          alert('Un compte existe déjà avec cet email.');
          return;
        }
        
        createAccount(email, password, name, 'admin');
        alert('Administrateur créé avec succès !');
        if(adminName) adminName.value = '';
        if(adminEmail) adminEmail.value = '';
        if(adminPassword) adminPassword.value = '';
        loadAdminData();
      });
    }

    if(logoutLink) {
      logoutLink.addEventListener('click', function(e) {
        e.preventDefault();
        clearUser();
        applyAuthState();
        if(dropdownMenu) dropdownMenu.classList.remove('show');
      });
    }

    if(profileBack) {
      profileBack.addEventListener('click', hideProfilePage);
    }

    if(logoutBtn) {
      logoutBtn.addEventListener('click', function() {
        clearUser();
        applyAuthState();
        hideProfilePage();
      });
    }

    // Form submission
    if(authForm) {
      authForm.addEventListener('submit', function(e) {
        e.preventDefault();
        console.log('Form submitted in mode:', currentMode);
        
        const email = authEmail ? authEmail.value.trim() : '';
        const password = authPassword ? authPassword.value.trim() : '';
        
        if(currentMode === 'signup') {
          const password2 = authPassword2 ? authPassword2.value.trim() : '';
          const name = authName ? authName.value.trim() : '';
          
          if(!name || !email || !password || !password2) {
            showMessage('Veuillez remplir tous les champs.');
            return;
          }
          
          if(password !== password2) {
            showMessage('Les mots de passe ne correspondent pas.');
            return;
          }
          
          // Validation inscription
          const signupValidation = validateSignup(email, password, name);
          if(!signupValidation.success) {
            showMessage(signupValidation.message);
            return;
          }
          
          // Créer le compte
          const newAccount = createAccount(email, password, name, 'user');
          setUser({ email: newAccount.email, name: newAccount.name, role: newAccount.role });
          showMessage('Compte créé avec succès !', 'success');
          
        } else {
          if(!email || !password) {
            showMessage('Veuillez remplir tous les champs.');
            return;
          }
          
          // Validation connexion
          const loginValidation = validateLogin(email, password);
          if(!loginValidation.success) {
            showMessage(loginValidation.message);
            return;
          }
          
          // Connexion réussie
          setUser({ email: loginValidation.account.email, name: loginValidation.account.name, role: loginValidation.account.role });
          showMessage('Connexion réussie !', 'success');
        }
        
        hideModal();
        if(authForm) authForm.reset();
        setMode('login');
        applyAuthState();
      });
    }

    // Make functions globally available
    window.deleteUser = deleteUser;
    window.openEditEmail = openEditEmail;
    window.openResetPassword = openResetPassword;
    window.createAdminAccount = function() {
      const adminAccount = {
        email: 'Mohfiill@gmail.com',
        password: 'Azertyadmin',
        name: 'Admin',
        role: 'admin',
        createdAt: new Date().toISOString()
      };
      const accounts = getAccounts();
      const existingIndex = accounts.findIndex(acc => acc.email === 'Mohfiill@gmail.com');
      if(existingIndex !== -1) {
        accounts[existingIndex] = adminAccount;
      } else {
        accounts.push(adminAccount);
      }
      saveAccounts(accounts);
      console.log('Admin account forced creation:', adminAccount);
      console.log('All accounts:', getAccounts());
      alert('Compte admin créé ! Vous pouvez maintenant vous connecter.');
    };

    // Initialize admin accounts if not exists
    function initializeAdminAccounts() {
      const accounts = getAccounts();
      
      // Liste des comptes admin par défaut
      const defaultAdmins = [
        {
          email: 'Mohfiill@gmail.com',
          password: 'Azertyadmin',
          name: 'Admin Principal',
          role: 'admin'
        },
        {
          email: 'support@minehost.fr',
          password: 'Support2024!',
          name: 'Support Admin',
          role: 'admin'
        },
        {
          email: 'tech@minehost.fr',
          password: 'Tech2024!',
          name: 'Équipe Technique',
          role: 'admin'
        }
      ];
      
      let createdCount = 0;
      defaultAdmins.forEach(adminData => {
        const exists = accounts.find(acc => acc.email === adminData.email);
        if(!exists) {
          accounts.push({
            ...adminData,
            createdAt: new Date().toISOString()
          });
          createdCount++;
          console.log('✅ Compte admin créé:', adminData.email);
        }
      });
      
      if(createdCount > 0) {
        saveAccounts(accounts);
        console.log(`🎉 ${createdCount} compte(s) administrateur créé(s) avec succès !`);
        console.log('📋 Tous les comptes:', getAccounts());
      } else {
        console.log('ℹ️ Tous les comptes admin existent déjà');
      }
    }

    // Initialize
    initializeAdminAccounts();
    setMode('login');
    applyAuthState();
    console.log('🚀 Auth script initialized - Comptes admin prêts !');
  });