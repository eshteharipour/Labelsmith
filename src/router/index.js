import { createRouter, createWebHistory } from "vue-router";
import Classifier from "@/views/Classifier.vue";
import Matcher from "@/views/Matcher.vue";

const routes = [
  { path: "/", component: Classifier },
  { path: "/matcher", component: Matcher },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
