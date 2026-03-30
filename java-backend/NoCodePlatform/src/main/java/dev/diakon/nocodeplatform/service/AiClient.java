package dev.diakon.nocodeplatform.service;

import lombok.Data;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.List;

@Service
public class AiClient {
    private final String PythonURL = "http://localhost:8000/train";
    private final String PredictURL = "http://localhost:8000/predict";
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

    @Data
    public static class PredictRequest {
        private List<Double> features;
        private String dataset;
    }

    @Data
    public static class PredictResponse {
        private Integer predicted_class;
        private String class_name;
        private List<Double> probabilities;
        private String error;
    }

    public PyResponse sendTrainingRequest(PyRequest request) {
        return restTemplate.postForObject(PythonURL, request, PyResponse.class);
    }

    public PredictResponse sendPredictRequest(PredictRequest request) {
        return restTemplate.postForObject(PredictURL, request, PredictResponse.class);
    }
}
