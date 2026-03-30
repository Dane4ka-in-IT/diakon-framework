package dev.diakon.nocodeplatform.service;

import lombok.Data;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.List;

@Service
public class AiClient {
    private final String PythonURL = "http://localhost:8000/train";
    private final RestTemplate restTemplate =  new RestTemplate();

    @Data
    public static class PyRequest{
        private List<Integer> layers;
        private String optimizer;
        private int epochs;
        private double learning_rate;
        private String dataset;
    }

    @Data
    public static class PyResponse {
        private String status;
        private String dataset;
        private List<Double> history;
    }

    public PyResponse sendTrainingRequest(PyRequest request) {
        return restTemplate.postForObject(PythonURL, request, PyResponse.class);
    }
}
