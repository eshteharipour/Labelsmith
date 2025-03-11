import { createRouter, createWebHistory } from "vue-router";
import Classifier from "@/views/Classifier.vue";
import Matcher from "@/views/Matcher.vue";
import Viewer from "@/views/Viewer.vue";

const routes = [
  { path: "/", component: Classifier },
  { path: "/matcher", component: Matcher },
  { path: "/viewer", component: Viewer },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
