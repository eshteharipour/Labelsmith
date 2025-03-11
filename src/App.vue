<template>
    <div class="app">
        <!-- Navigation links -->
        <nav>
            <router-link to="/">Classifier</router-link> |
            <router-link to="/matcher">Matcher</router-link> |
            <router-link to="/viewer">Viewer</router-link>
        </nav>

        <router-view></router-view>
    </div>
</template>

<style>
.app {
    padding: 20px;
}

nav {
    margin-bottom: 20px;
}

nav a {
    margin-right: 10px;
    text-decoration: none;
}

nav a.router-link-active {
    font-weight: bold;
}
</style>