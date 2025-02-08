<template>
    <div>
        <!-- Navbar -->
        <nav class="navbar">
            <div class="navbar-left">
                <img src="../assets/orca.png" alt="Logo" class="navbar-logo" />
            </div>
            <div class="navbar-center">
                <div class="navbar-brand">Orca</div>
            </div>
            <ul class="navbar-links">
                <li v-if="!isLoggedIn"><a @click="navigate('login')">Login</a></li>
                <li v-if="!isLoggedIn"><a @click="navigate('register')">Register</a></li>
                <li v-if="isLoggedIn">
                    <a class="dropdown-toggle">Account</a>
                    <ul class="dropdown-menu">
                        <li><a @click="navigate('profile')">Profile</a></li>
                        <li><a @click="navigate('logout')">Logout</a></li>
                    </ul>
                </li>
            </ul>
        </nav>

        <!-- Progress Bar -->
        <div class="progress-bar-container">
            <div class="progress-bar" :style="{ width: progress + '%' }"></div>
        </div>

        <!-- Hub Container -->
        <div class="hub-container">
            <h1 class="main-heading">Setting Up an AWS Cloud User</h1>

            <!-- Steps -->
            <div v-for="(step, index) in steps" :key="index" class="step-card" @click="toggleStep(index)">
                <h2 class="step-title">{{ step.title }}</h2>
                <div v-if="activeStep === index" class="step-content">
                    <p v-html="step.content"></p>
                    <pre v-if="step.policy">{{ JSON.stringify(step.policy, null, 2) }}</pre>

                    <!-- Button for Step 6 -->
                    <button
                        v-if="step.requiresUpload"
                        class="upload-button"
                        @click.stop="navigateToUpload"
                    >
                        Upload Cloud Credentials
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>


<script>
import { steps } from "@/assets/steps";
import "@/assets/css/aws-setup-tutorial.css";

export default {
    data() {
        return {
            isLoggedIn: false,
            activeStep: null,
            steps: steps,
            progress: 0
        };
    },
    methods: {
        navigate(page) {
            this.$router.push(`/${page}`);
        },
        checkLogin() {
            const token = sessionStorage.getItem("token");
            this.isLoggedIn = !!token;
        },
        toggleStep(index) {
            this.activeStep = this.activeStep === index ? null : index;
            this.updateProgress();
        },
        updateProgress() {
            const completedSteps = this.steps.filter((_, index) => index <= this.activeStep).length;
            this.progress = (completedSteps / this.steps.length) * 100;
        },
        navigateToUpload() {
            this.$router.push('/link');  // Navigate to the upload page
        }
    },
    mounted() {
        this.checkLogin();
    }
};
</script>

